# Функции для транскрибации видео в текст


# # from moviepy.editor import VideoFileClip
# import torch
# from transformers import AutoProcessor, pipeline, AutoModelForSpeechSeq2Seq
# from datasets import Dataset
# from torch.utils.data import DataLoader


# def create_audio_to_text_pipe(audios):
#     device = "cuda:0" if torch.cuda.is_available() else "cpu"
#     print('device:', device)
#     torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
#     model_id = "openai/whisper-small"


#     data = {
#         'audio_name': audios
#     }

#     dataset = Dataset.from_dict(data)
#     dataloader = DataLoader(dataset, batch_size=16, shuffle=False)

#     model = AutoModelForSpeechSeq2Seq.from_pretrained(
#         model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=False
#     )
#     model.to(device)

#     processor = AutoProcessor.from_pretrained(model_id)


#     audio_to_text_pipe = pipeline(
#         "automatic-speech-recognition",
#         model=model,
#         tokenizer=processor.tokenizer,
#         feature_extractor=processor.feature_extractor,
#         max_new_tokens=128,
#         chunk_length_s=30,
#         batch_size=16,
#         return_timestamps=True,
#         torch_dtype=torch_dtype,
#         device=device,
#     )

#     return dataloader, audio_to_text_pipe


# # def wav_to_text(audios, pipe):
# #     chunks = pipe(audios, batch_size=16)['chunks']
# #     return chunks


# # for batch in tqdm(dataloader_index):
# #     names = batch['audio_name']
# #     # 1/0
# #     res = pipe(batch['audio_name'], batch_size=16)
# #     for name, r in zip(names, res):
# #         RESULT_FILE_PATH = f"index_text/{name.split('/')[-1][:-4]}.pickle"
# #         with open(RESULT_FILE_PATH, 'wb') as f:
# #             pickle.dump(r, f)


#    # audio.write_audiofile(wav_file)

# # for video in tqdm(os.listdir('compressed_index')):
# #     VIDEO_FILE_PATH = f"compressed_index/{video}"
# #     AUDIO_FILE_PATH = f"index_audio_wav/{video[:-4]}.wav"

# #     audio = mp4_to_wav(VIDEO_FILE_PATH, AUDIO_FILE_PATH)
