import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

import cv2

import os
import time
import uuid
from glob import glob
from tqdm import tqdm
import math
from collections import defaultdict

import torch
import torch.nn
from transformers import ViTImageProcessor, ViTModel


class FindPiracy:

  def __init__(self, piracy_id, candidates, root_path, device="cuda"):

    self.piracy_id = root_path + "compressed_val/" + piracy_id + '.mp4'
    self.candidates = candidates
    self.root_path = root_path
    self.device = torch.device(device)

  def init_model(self, hf_path='google/vit-base-patch16-224-in21k'):

    self.processor = ViTImageProcessor.from_pretrained(hf_path)
    self.model = ViTModel.from_pretrained(hf_path)

    self.model = self.model.eval()

  def eval_index_path(self, eval_string):

      return eval_string.replace(
                                  "A_jupyter_lab\\ЛЦТ\\index_audio_wav\\",
                                  self.root_path + "index/compressed_index/"
                                ) \
                        .replace("wav", "mp4")


  @torch.no_grad()
  def __call__(self, frame_window):

    similarities_result = defaultdict(list)

    for i, (video_path, values) in enumerate(self.candidates.items()):

      print(f"candidate {i} started")

      evaled_license_path = self.eval_index_path(video_path)

      cap_piracy = cv2.VideoCapture(self.piracy_id)
      cap_license = cv2.VideoCapture(evaled_license_path)

      # getting frames each N seconds of the video

      # 1 способ

      num_cur_piracy_frame = math.floor(values[1]) * 10
      num_cur_license_frame = math.floor(values[3]) * 10

      cap_piracy.set(cv2.CAP_PROP_POS_FRAMES, num_cur_piracy_frame)
      cap_license.set(cv2.CAP_PROP_POS_FRAMES, num_cur_license_frame)

      similarities = []

      frame_window = frame_window

      for i in tqdm(range(0, (math.ceil(values[2]) - math.floor(values[1])) * 10)):

            _, piracy_frame = cap_piracy.read()
            _, license_frame = cap_license.read()

            if i % frame_window == 0:

              # getting piracy frame embedding
              inputs_piracy = self.processor(images=torch.tensor(piracy_frame), return_tensors="pt")
              inputs_piracy["pixel_values"] = inputs_piracy["pixel_values"].to(self.device)

              outputs_piracy = self.model(**inputs_piracy)
              piracy_embedding = outputs_piracy.pooler_output.squeeze(0)

              # getting license frame embedding
              inputs_lisense = self.processor(images=torch.tensor(license_frame), return_tensors="pt")
              inputs_lisense["pixel_values"] = inputs_lisense["pixel_values"].to(self.device)

              outputs_license = self.model(**inputs_lisense)
              license_embedding = outputs_license.pooler_output.squeeze(0)

              cos = torch.nn.CosineSimilarity(dim=0)

              similarities.append(cos(piracy_embedding, license_embedding).item())


      similarities_result[evaled_license_path] = similarities
      print(f"candidate {i} finished")

    return similarities_result
  
#пример использования
  
#   candidates = {
#  'A_jupyter_lab\\ЛЦТ\\index_audio_wav\\0ea016128113476c741eba66ecbb5f0a.wav': (1094,
#   530.1716553287982,
#   767.0233560090703,
#   554.1716553287982,
#   791.0233560090703),
#  'A_jupyter_lab\\ЛЦТ\\index_audio_wav\\fe8ac2d7f57582ac5665692813d76efa.wav': (787,
#   530.1716553287982,
#   767.0233560090703,
#   554.1716553287982,
#   791.0233560090703),
#  }

# piracy_index = "4yf1e6h236n00lp7ckc80j01fwubylnn"

# finder = FindPiracy(piracy_id=piracy_index, candidates=candidates, root_path="../data/", device="cpu")

#finder(50) возвращает покадровые cos_similarity с шагом 50 для каждого проверяемого видео 