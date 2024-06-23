import uuid
import numpy as np
import logging
from . import settings
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter
from .storage import store_video, get_matches, get_info_for_video_id, video_in_db, checkpoint_db
# from .audio2text import create_audio_to_text_pipe
import time
import os, pickle
from tqdm import tqdm
from multiprocessing import Pool, Lock, current_process


def get_video_info(filename):
    """Возвращает id видео по пути к нему. В дальнейшем можно будет также возвращать название, автора и т.д.

    :param filename: Путь к файлу
    :returns: название файла
    """
    return filename.split('/')[-1]


def mp4_to_wav(mp4_file, wav_file):
    """Принимает видео, записывает видео из него в wav файл

     :param mp4_file: Путь к видео
     :param wav_file: Путь, в который записать аудио
     """
    assert mp4_file[-3:] == 'mp4'

    video = VideoFileClip(mp4_file, audio_fps=44100 // 4)
    audio = video.audio

    audio.write_audiofile(wav_file)


def file_to_spectrogram(filename):
    """Создает спектограмму с нужным SAMPLE_RATE и FFT_WINDOW_SIZE

    :param filename: Путь к аудио файлу
    :returns: * f - np.array частот
              * t - np.array временных отрезков
              * Sxx - np.array "мощностей" каждой пары время/частота
    """
    a = AudioSegment.from_file(filename).set_channels(1).set_frame_rate(settings.SAMPLE_RATE)
    audio = np.frombuffer(a.raw_data, np.int16)
    nperseg = int(settings.SAMPLE_RATE * settings.FFT_WINDOW_SIZE)
    return spectrogram(audio, settings.SAMPLE_RATE, nperseg=nperseg)


def find_peaks(Sxx):
    """Ищет пики в спектограмме

    :param Sxx: Спектограмма
    :returns: list of tuples (пики в формате (частота, время))
    """
    data_max = maximum_filter(Sxx, size=settings.PEAK_BOX_SIZE, mode='constant', cval=0.0)
    peak_goodmask = (Sxx == data_max)  # пики помечаем значениями True
    y_peaks, x_peaks = peak_goodmask.nonzero()
    peak_values = Sxx[y_peaks, x_peaks]
    i = peak_values.argsort()[::-1]
    j = [(y_peaks[idx], x_peaks[idx]) for idx in i]
    total = Sxx.shape[0] * Sxx.shape[1]

    peak_target = int((total / (settings.PEAK_BOX_SIZE ** 2)) * settings.POINT_EFFICIENCY)  # Сколько пиков оставим
    return j[:peak_target]


def idxs_to_tf_pairs(idxs, t, f):
    """Индексы времени/частот -> время/частоты"""
    return np.array([(f[i[0]], t[i[1]]) for i in idxs])


def hash_point_pair(p1, p2):
    """Переводим пару двух точек (время, частота) в хэш"""
    return hash((p1[0], p2[0], p2[1] - p2[1]))


def target_zone(anchor, points, width, height, t):
    """Генерируем таргет-зону для формирования пар двух пиков


    :param anchor: Точка, для которой создаем пары
    :param points: Возможные точки
    :param width: Ширина таргет-зоны
    :param height: Высота таргет-зоны
    :param t: Секунд между началом таргет-зоны и точкой
    :returns: Генерирует все возможные точки-пары
    """
    x_min = anchor[1] + t
    x_max = x_min + width
    y_min = anchor[0] - (height * 0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point


def hash_points(points, filename):
    """Создаем хэши для пиков (для каждого пика формируем пары с другими пиками из таргет-зоны)

    :param points: Список пиков
    :param filename: Название видео
    :returns: Список кортежей вида (хэш пары пиков, разница во времени между двумя пиками, video_id)
    """
    hashes = []
    video_id = uuid.uuid5(uuid.NAMESPACE_OID, filename).int
    for anchor in points:
        for target in target_zone(
                anchor, points, settings.TARGET_T, settings.TARGET_F, settings.TARGET_START
        ):
            hashes.append((
                hash_point_pair(anchor, target),
                anchor[1],
                target[1],
                str(video_id)
            ))
    return hashes


def fingerprint_file(filename):
    """Генеририуем хэш из файла

    :param filename: Путь к файлу
    :returns: Выход функции hash_points
    """
    f, t, Sxx = file_to_spectrogram(filename)
    peaks = find_peaks(Sxx)
    peaks = idxs_to_tf_pairs(peaks, t, f)
    return hash_points(peaks, filename)


def register_video(file_path):
    """Индексируем 1 видео

    :param file_path: Путь к файлу"""

    AUDIO_FILE_PATH = f"cache/{file_path.rsplit('/', 1)[1][:-4]}.wav"
    if video_in_db(AUDIO_FILE_PATH):  # Если видео уже есть в БД
        return

    mp4_to_wav(file_path, AUDIO_FILE_PATH)  # Видео -> wav

    logging.info(f"{current_process().name} converted to audio {file_path}")

    logging.info(f"{current_process().name} started fingerprinting {AUDIO_FILE_PATH}")

    hashes = fingerprint_file(AUDIO_FILE_PATH)
    video_info = get_video_info(AUDIO_FILE_PATH)

    try:
        logging.info(f"{current_process().name} waiting to write {AUDIO_FILE_PATH}")
        with lock:
            logging.info(f"{current_process().name} writing {AUDIO_FILE_PATH}")
            store_video(hashes, video_info)
            logging.info(f"{current_process().name} wrote {AUDIO_FILE_PATH}")
    except NameError:
        logging.info(f"Single-threaded write of {file_path}")
        store_video(hashes, video_info)


def pool_init(l):
    """
    Синхронизируем запись данных в БД sqlite
    """
    global lock
    lock = l
    logging.info(f"Pool init in {current_process().name}")


def register_directory(path):
    """
    Индексируем целую папку
    """

    to_register = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] != 'mp4':
                continue

            file_path = root + '/' + f

            to_register.append(file_path)
    l = Lock()
    with Pool(settings.NUM_WORKERS, initializer=pool_init, initargs=(l,)) as p:
        # Параллельно индексируем видео
        p.map(register_video, to_register)

    checkpoint_db()

    # Транскрибируем аудио в текст

    # dataloader, audio_to_text_pipe = create_audio_to_text_pipe([f"cache/{file_path.rsplit('/', 1)[1][:-4]}.wav" for file_path in to_register])

    # for batch in tqdm(dataloader):
    #     names = batch['audio_name']
    #     results = audio_to_text_pipe(batch['audio_name'], batch_size=16)
    #     for name, res in zip(names, results):
    #         RESULT_FILE_PATH = f"index_text/{name.split('/')[-1][:-4]}.pickle"
    #         with open(RESULT_FILE_PATH, 'wb') as f:
    #             pickle.dump(res['chunks'], f)
    #         os.remove(name)
