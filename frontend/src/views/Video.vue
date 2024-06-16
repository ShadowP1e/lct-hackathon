<template>
  <div v-if="finish" class="center" style="margin-top: 50px">
    <div class="video">
      <h2>Видео {{video_id}}</h2>

      <video
          controls
          preload="auto"
          width="700"
          height="400"
          data-setup="{}"
      >
        <source :src="video_url" />
      </video>

    </div>
    <div v-if="video_copyright_parts.length > 0" class="copyright-parts">
      <h2>Лицензионный контент</h2>

      <div class="accordion">
        <div class="accordion-item" v-for="(item, index) in video_copyright_parts" :key="index">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" @click="clickAccordion" :id="item.id" type="button">
              {{~~(item.start / 60)}}:{{addLeadingZero(item.start % 60)}} - {{~~(item.end / 60)}}:{{addLeadingZero(item.end % 60)}}
            </button>
          </h2>
          <div class="accordion-collapse collapse" :id="'content-' + item.id">
            <div class="accordion-body">

              <video
                  controls
                  preload="auto"
                  width="400"
                  height="250"
                  data-setup="{}"
              >
                <source :src="item.url" />
              </video>
              <p>Источник: {{item.from_filename}}.mp4 </p>
            </div>
          </div>
        </div>
      </div>

    </div>
    <div v-else class="copyright-parts">
      <h2>
        Видео не содержит лицензионного контента
      </h2>
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
  name: "Video",
  setup(){
    const router = useRouter();
    const video_id = router.currentRoute.value.params.id

    const finish = ref(false);
    const video_url = ref(null);
    const video_copyright_parts = ref(null)
    let pollingInterval = null;

    const addLeadingZero = (number) => {
      return number < 10 ? '0' + number : number.toString();
    }

    const pollServer = async () => {
      axiosInstance.get(`/videos/${video_id}`, {withCredentials: true})
          .then((response) => {
            console.log(response.data)
            if (response.data.finished){
              finish.value = true;
              video_url.value = response.data.url;
              video_copyright_parts.value = response.data.copyright_video_parts;
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

    const clickAccordion = async (e) => {
      var button = document.getElementById(e.target.id);
      var content = document.getElementById('content-' + e.target.id);

      if (content.classList.contains('show')) {
        content.classList.remove('show')
        button.classList.add('collapsed')
      }
      else{
        content.classList.add('show')
        button.classList.remove('collapsed')
      }

      console.log(e.target.id)
    }

    return{
      video_id,
      finish,
      video_url,
      video_copyright_parts,
      clickAccordion,
      addLeadingZero,
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
  flex-direction: column;
  vertical-align: center;
  horiz-align: center;
}

.video{
  text-align: center;
}
.copyright-parts{
  text-align: center;
  width: 60vw;
  margin: 0 auto;
}

</style>