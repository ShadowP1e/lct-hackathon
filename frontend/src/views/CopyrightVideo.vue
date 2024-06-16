<template>
  <div v-if="finish" class="center" style="margin-top: 50px">
    <div class="message">
      <h1>Видео успешно добавленно</h1>
      <div style="display: flex; flex-direction: column; align-items: center">
        <video
            controls
            preload="auto"
            width="700"
            height="400"
            data-setup="{}"
        >
          <source :src="video_url" />
        </video>
        <button @click="accept" class="w-50 btn btn-lg btn-primary mt-3" type="submit">Принять</button>
      </div>
    </div>
  </div>

  <div v-else class="loader-div">
    <div style="display: flex; justify-content: center"><div id="loader"></div></div>
    <h2 class="loader-text">Видео обрабатывается</h2>
    <h2 class="loader-text">ID видео: {{video_id}}</h2>
  </div>
</template>


<script>
import {useRouter} from "vue-router";
import {onMounted, onUnmounted, ref} from "vue";
import axiosInstance from "@/axiosInstance";

export default {
  name: "CopyrightVideo",
  setup(){
    const router = useRouter();
    const video_id = router.currentRoute.value.params.id

    const finish = ref(false);
    const video_url = ref(null);
    const video_copyright_parts = ref(null)
    let pollingInterval = null;

    const pollServer = async () => {
      axiosInstance.get(`/copyright-videos/${video_id}`, {withCredentials: true})
          .then((response) => {
            console.log(response.data)
            if (response.data.finished){
              video_url.value = response.data.url;
              finish.value = true;
              clearInterval(pollingInterval);
            }
          })
          .catch((error) => {
            console.log(error.response.data);
          })
    };

    onMounted(() => {
      pollServer()
      pollingInterval = setInterval(pollServer, 3000); // Интервал опроса в миллисекундах
    });

    onUnmounted(() => {
      clearInterval(pollingInterval); // Очищаем интервал при уничтожении компонента
    });

    const accept = async () => {
      router.push('/upload-copyright-video')
    }

    return{
      video_id,
      finish,
      video_url,
      video_copyright_parts,
      accept,
    }
  }
}
</script>

<style scoped>
#loader {
  z-index: 1;
  width: 120px;
  height: 120px;
  border: 16px solid #f3f3f3;
  border-radius: 50%;
  border-top: 16px solid #3498db;
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

/* Add animation to "page content" */
.animate-bottom {
  position: relative;
  -webkit-animation-name: animatebottom;
  -webkit-animation-duration: 1s;
  animation-name: animatebottom;
  animation-duration: 1s
}

@-webkit-keyframes animatebottom {
  from { bottom:-100px; opacity:0 }
  to { bottom:0px; opacity:1 }
}

@keyframes animatebottom {
  from{ bottom:-100px; opacity:0 }
  to{ bottom:0; opacity:1 }
}
.loader-text{
  text-align: center;
}
.loader-div{
  margin-top: 30vh;
  width: 100vw;
}
.center{
  display: flex;
  justify-content: center;
  vertical-align: center;
  horiz-align: center;
}

.message{
  text-align: center;
  width: 80vw;
}

</style>