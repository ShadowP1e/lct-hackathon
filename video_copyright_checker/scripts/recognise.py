import os
import logging
from multiprocessing import Pool, Lock, current_process
import numpy as np
import pandas as pd
from . import settings
from .fingerprint import mp4_to_wav, register_video, register_directory, fingerprint_file, get_video_info
from .storage import store_video, get_matches, get_info_for_video_id, video_in_db, checkpoint_db
# from .audio2text import create_audio_to_text_pipe
import time
from collections import Counter
import pickle
import re

KNOWN_EXTENSIONS = ["mp3", "wav", "flac", "m4a"]  # Доступные расширения


# IoU для текстов из 2 фрагментов

# def get_text_IoU(check_text, license_file, start_time_piracy, end_time_piracy, start_time_license, end_time_license):

#     # with open(f'C:\\Users\\777\\A_jupyter_lab\\ЛЦТ\\val_text\\{check_file}.pickle', 'rb') as f:

#     # with open(f'C:\\Users\\777\\A_jupyter_lab\\ЛЦТ\\index_text\\{license_file}.pickle', 'rb') as f:
#     with open(license_file, 'rb') as f:
#         license_text = pickle.load(f)

#     check_text_sample = ''.join([chunk['text'] for chunk in check_text[:-1] if (chunk['timestamp'][1] >=start_time_piracy and chunk['timestamp'][0] <= end_time_piracy)]).lower()
#     license_text = ''.join([chunk['text'] for chunk in license_text[:-1] if (chunk['timestamp'][1] >=start_time_license and chunk['timestamp'][0] <= end_time_license)]).lower()
#     check_text_sample = re.sub(rf'(\W)', rf' \1 ', check_text_sample)
#     license_text = re.sub(rf'(\W)', rf' \1 ', license_text)
#     intercept = len(set(license_text.split()) & set(check_text_sample.split()))
#     IoU = intercept/(len(set(license_text.split())) + len(set(check_text_sample.split())) - intercept) if intercept!=0 else 0
#     return IoU


def score_match(offsets):
    """
    Находим число совпадений проверяемого видео с лицензионным видео

    :param offsets: список разниц во времени между совпавшими хэшами
    :returns: Максимальное число совпадений с одной и той же разницей во времени между ними
    :rtype: int
    """

    binwidth = 1  # с какой точностью в секундах считаем разницу во времени
    tks = list(map(lambda x: x[0] - x[1], offsets))

    bins = np.arange(int(min(tks)), int(max(tks)) + binwidth + 1, binwidth)

    digitized_tks = np.digitize(tks, bins)

    most_common = Counter(digitized_tks).most_common()[0]
    id_max, count_max = most_common[0], most_common[1]
    diff = bins[id_max]

    start_time_piracy = float('inf')
    end_time_piracy = -1

    for offset, digitized_tk in zip(offsets, digitized_tks):
        if digitized_tk == id_max:
            start_time_piracy = min(start_time_piracy, offset[1])
            end_time_piracy = max(end_time_piracy, offset[2])

    start_time_license = start_time_piracy + diff
    end_time_license = end_time_piracy + diff

    return count_max, start_time_piracy, end_time_piracy, start_time_license, end_time_license


def best_match(matches, top_k):
    """Находим видео с top_k совпадений

    :param matches: Dict {video_id: разницы во времени между совпадениями}
    :param top_k: Число совпавших видео

    :returns: Dict {video_id: score, start_time_piracy, end_time_piracy, start_time_license, end_time_license} / None (если нет кандидатов)
    :rtype: str
    """
    matched_video = None
    start_time_piracy, end_time_piracy, start_time_license, end_time_license = None, None, None, None
    results = {}
    best_scores = [(0, 0)] * top_k  # (video_id, score)
    matches = {k: v for k, v in sorted(matches.items(), key=lambda item: -len(item[1]))}
    for video_id, offsets in matches.items():
        if len(offsets) <= max(min(score for id, score in best_scores), 40):
            # Слишком мало совпадений
            continue
        score, *times = score_match(offsets)
        if score > max(min(score for id, score in best_scores), 40):
            start_time_piracy, end_time_piracy, start_time_license, end_time_license = times
            if end_time_piracy - start_time_piracy <= 10: continue

            if best_scores[0][0] in results:
                del results[best_scores[0][0]]

            best_scores = best_scores[1:] + [(video_id, score)]
            best_scores.sort(key=lambda x: x[1])
            results[video_id] = (score, start_time_piracy, end_time_piracy, start_time_license, end_time_license)
    if best_scores[-1][1] == 0:
        return None

    return results


# Считаем IoU для текстов, умножаем на число совпадений, находим самого вероятного кандидата

# def multiply_score_by_text_IoU(results_with_video_name, check_text):

#     best_score, best_file = 40, None
#     times = []

#     for license_file, (score, start_time_piracy, end_time_piracy, start_time_license, end_time_license) in results_with_video_name.items():
#         license_file = license_file.replace('.wav', '.pickle')
#         license_file = 'index_text/' + license_file
#         if score <= best_score: continue
#         IoU = get_text_IoU(check_text, license_file, start_time_piracy, end_time_piracy, start_time_license, end_time_license)
#         final_score = IoU * score
#         if final_score > best_score:
#             final_score = final_score
#             best_file = license_file.rsplit('/', 1)[1].rsplit('.', 1)[0]
#             times = [start_time_piracy, end_time_piracy, start_time_license, end_time_license]

#     return best_file, times


def recognise_video(filename):
    """Проверяем видео на наличие плагиата

    :param filename: Путь к файлу
    :returns: (None, None) или (video_id, (start_time_piracy, end_time_piracy, start_time_license, end_time_license))
    """
    AUDIO_FILE_PATH = f"cache/{filename.rsplit('/', 1)[1][:-4]}.wav"
    mp4_to_wav(filename, AUDIO_FILE_PATH)

    hashes = fingerprint_file(AUDIO_FILE_PATH)
    matches = get_matches(hashes)
    results = best_match(matches, top_k=1)
    if results is None:
        os.remove(AUDIO_FILE_PATH)
        return None, None

    # Получаем текст из видео
    # _, audio_to_text_pipe = create_audio_to_text_pipe([AUDIO_FILE_PATH])

    # text = audio_to_text_pipe(AUDIO_FILE_PATH, batch_size=32)['chunks']
    # os.remove(AUDIO_FILE_PATH)

    results_with_video_name = dict()
    for matched_video in results.keys():
        info = get_info_for_video_id(matched_video)
        results_with_video_name[info[0]] = results[matched_video]

    # result, times = multiply_score_by_text_IoU(results_with_video_name, text)
    return list(results_with_video_name.keys())[0].replace('.wav', ''), list(results_with_video_name.values())[0][1:]


def recognise_directory(path):
    """Проверяем все видео в папке на наличие плагиата

    :param path: Путь к папке
    :returns: pd.DataFrame со столбцами ['ID-piracy', 'SEG-piracy', 'ID-license', 'SEG-license']
    """

    to_check = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.split('.')[-1] != 'mp4':
                continue
            file_path = root + '/' + f

            to_check.append(file_path)
    preds = []
    for check_file in to_check:
        result, times = recognise_video(check_file)

        if result is not None:
            preds.append({'check_file': check_file, 'license_file': result, 'start_time_piracy': times[0],
                          'end_time_piracy': times[1],
                          'start_time_license': times[2], 'end_time_license': times[3]})
    pred_df = []

    for pred in preds:
        pred_df.append([pred['check_file'].rsplit('/', 1)[1],
                        f"{int(pred['start_time_piracy'])}-{int(pred['end_time_piracy']) + 1}",
                        pred['license_file'] + '.mp4',
                        f"{int(pred['start_time_license'])}-{int(pred['end_time_license']) + 1}"])
    pred_df = pd.DataFrame(pred_df)
    pred_df.columns = ['ID-piracy', 'SEG-piracy', 'ID-license', 'SEG-license']
    pred_df.to_csv('preds.csv', index=False)

    return pred_df

