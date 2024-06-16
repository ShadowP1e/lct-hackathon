<template>
  <Forbidden v-if="!store.getters.userIsLoggedIn"/>
  <div v-else>
    <div class="center" style="margin-top: 100px">
      <div class="upload_form">
        <h2>Загрузить лицензионное видео</h2>
        <form @submit.prevent="submit" method="POST" enctype="multipart/form-data">
          <div>
            <label for="file" class="drop-container" id="dropcontainer">
              <span class="drop-title">Drop files here</span>
              <input type="file" id="file" name="file" required>
            </label>
          </div>
          <div class="submit-container">
            <input type="submit" class="submit" value="Отправить">
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import Forbidden from "@/views/Forbidden";
import {useStore} from "vuex";
import {useRouter} from "vue-router";
import axiosInstance from "@/axiosInstance";


export default {
  name: "UploadCopyrightVideo",
  components: {Forbidden, },
  setup(){
    const store = useStore();
    const router = useRouter();

    const extractIds = (response) => {
      return response.map(video => video.id).join('&video=');
    };

    const submit = (e) => {
      const form = new FormData(e.target);

      axiosInstance.post('/copyright-videos/upload', form, {withCredentials: true})
          .then((response) => {
            console.log(response.data)
            if (Array.isArray(response.data)){
              let ids = extractIds(response.data)
              router.push(`/copyright-videos?video=` + ids)
            }else {
              router.push(`/copyright-video/${response.data.id}`)
            }
          })
          .catch((error) => {
            console.log(error.response.data)
          })
    }

    return{
      store,
      router,
      submit
    }
  }

}
</script>

<style scoped>
.drop-container {
  background-color: white;
  position: relative;
  display: flex;
  gap: 10px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 200px;
  padding: 20px;
  border-radius: 10px;
  border: 2px dashed #555;
  color: #444;
  cursor: pointer;
  transition: background .2s ease-in-out, border .2s ease-in-out;
}

.drop-container:hover,
.drop-container.drag-active {
  background: #eee;
  border-color: #111;
}

.drop-container:hover .drop-title,
.drop-container.drag-active .drop-title {
  color: #222;
}

.drop-title {
  color: #444;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  transition: color .2s ease-in-out;
}

input[type=file] {
  width: 350px;
  max-width: 100%;
  color: #444;
  padding: 5px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #555;
}

input[type=file]::file-selector-button {
  margin-right: 20px;
  border: none;
  background: #084cdf;
  padding: 10px 20px;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  transition: background .2s ease-in-out;
}

input[type=file]::file-selector-button:hover {
  background: #0d45a5;
}

.center{
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto;
  max-width: 500px;
}

.upload_form {
  margin-left: 10px;
  margin-right: 10px;
}

.submit{
  border: none;
  text-decoration: none;
  background-color: #084cdf;
  width: 100px;
  height: 50px;
  color: white;
  cursor: pointer;
  border-radius: 10px;
  transition: background .2s ease-in-out;
}
.submit:hover{
  background: #0d45a5;
}

.submit-container{
  margin-top: 10px;
  display: flex;
  justify-content: right;
}

</style>