<template>
  <div class="d-flex flex-column flex-md-row p-4 gap-4 py-md-5 align-items-center justify-content-center">
    <div class="list-group">

      <a v-for="video in videos" :key="video.id" :href="'/copyright-video/' + video.id" class="list-group-item list-group-item-action d-flex gap-3 py-3" aria-current="true">
        <div class="d-flex gap-2 w-100 justify-content-between">
          <div>
            <h6 class="mb-0">{{ video.id }}</h6>
            <p class="mb-0 opacity-75">{{ video.filename }}</p>
          </div>
          <div v-if="video.finished">
            <p>✔️</p>
          </div>
          <div v-else class="loader-div">
            <div style="display: flex; justify-content: center"><div id="loader"></div></div>
          </div>
        </div>
      </a>

    </div>
  </div>
</template>

<script>
import {useRoute} from "vue-router";
import {onMounted, onUnmounted, ref} from "vue";
import axiosInstance from "@/axiosInstance";

export default {
  name: "CopyrightVideos",
  setup() {
    const route = useRoute();
    const videos = ref([]);

    const fetchVideoStatus = async (id) => {
      try {
        const response = await axiosInstance.get(`http://localhost:8000/api/copyright-videos/${id}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching video status:', error);
        return null;
      }
    };

    const updateVideoStatuses = async () => {
      const videoIds = route.query.video || [];
      const newVideos = await Promise.all(videoIds.map(async (id) => {
        const statusData = await fetchVideoStatus(id);
        return {
          id,
          filename: statusData.filename,
          finished: statusData.finished,
        };
      }));
      console.log(videos)
      videos.value = newVideos;
    };

    let intervalId;
    onMounted(() => {
      updateVideoStatuses(); // Initial fetch
      intervalId = setInterval(updateVideoStatuses, 3000); // Fetch every 3 seconds
    });

    onUnmounted(() => {
      clearInterval(intervalId);
    });

    return {
      videos,
    };
  }
}
</script>

<style scoped>
#loader {
  z-index: 1;
  width: 30px;
  height: 30px;
  border: 8px solid #f3f3f3;
  border-radius: 50%;
  border-top: 8px solid #3498db;
  -webkit-animation: spin 2s linear infinite;
  animation: spin 2s linear infinite;
}

@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@-webkit-keyframes animatebottom {
  from { bottom:-100px; opacity:0 }
  to { bottom:0px; opacity:1 }
}

@keyframes animatebottom {
  from{ bottom:-100px; opacity:0 }
  to{ bottom:0; opacity:1 }
}
</style>