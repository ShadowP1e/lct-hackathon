<template>
  <header class="p-3 bg-dark text-white">
    <div class="container">
      <div class="d-flex flex-wrap align-items-center justify-content-center justify-content-lg-start">
        <ul class="nav col-12 col-lg-auto me-lg-auto mb-2 justify-content-center mb-md-0">
          <li>
            <router-link to="/" class="nav-link px-2 text-white">Проверить видео</router-link>
          </li>
          <li v-show="userIsLoggedIn">
            <router-link to="/upload-copyright-video" class="nav-link px-2 text-white">Загрузить видео в базу</router-link>
          </li>
        </ul>

        <div class="text-end">
          <router-link v-show="!userIsLoggedIn" to="/login" class="btn btn-outline-light me-2">Вход</router-link>
          <button v-show="userIsLoggedIn" @click="logout" class="btn btn-outline-light me-2">Выход</button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import {useRouter} from "vue-router";
import {useStore} from "vuex";
import {computed} from "vue";
import axiosInstance from "@/axiosInstance";

export default {
  name: "Header",
  setup() {
    const router = useRouter();
    const store = useStore();

    const userIsLoggedIn = computed(() => store.getters.userIsLoggedIn);

    const logout = async () => {
      await store.dispatch('setUserLoggedIn', false);
      await store.dispatch('setUserRole', '');

      await axiosInstance.post('/auth/logout', {}, {withCredentials: true});

      axiosInstance.defaults.headers.common['Authorization'] = '';

      await router.push('/login');
    }

    return {
      userIsLoggedIn,
      logout
    }
  }
}
</script>

<style scoped>

</style>