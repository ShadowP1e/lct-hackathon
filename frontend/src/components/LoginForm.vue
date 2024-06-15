<template>
  <h1 class="text-center h3 mb-3 fw-normal">Вход</h1>

  <form @submit.prevent="submit">
    <div class="form-floating">
      <input type="email" class="form-control" :class="{'is-invalid': !isValidForm }" name="email" placeholder="name@example.com">
      <label>Email</label>
    </div>

    <div class="form-floating">
      <input type="password" class="form-control" :class="{'is-invalid': !isValidForm }" name="password" placeholder="Password">
      <label>Пароль</label>
    </div>

    <div v-if="!isValidForm">
      <p style="margin-top: 10px; color: #dc3545; text-align: justify">{{formError}}</p>
    </div>

    <button class="w-100 btn btn-lg btn-primary" type="submit">Submit</button>

  </form>
</template>

<script>
import {useRouter} from "vue-router";
import {useStore} from "vuex";
import {onUnmounted, ref} from "vue";
import axiosInstance from "@/axiosInstance";

export default {
  name: "LoginForm",
  setup() {
    const formError = ref('');
    const isValidForm = ref(true);
    const router = useRouter();
    const store = useStore();

    const resetForm = () => {
      formError.value = ''
      isValidForm.value = true
    }

    onUnmounted(() => {
      resetForm()
    });

    const submit = (e) => {
      resetForm()
      const form = new FormData(e.target);

      const inputs = Object.fromEntries(form.entries());

      axiosInstance.post('/users/login', inputs, {withCredentials: true})
          .then((response) => {
            console.log(response.data)
            axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${response.data.tokens.access_token}`;

            store.dispatch('setUserLoggedIn', true)

            router.push('/upload-copyright-video');
          })
          .catch((error) => {
            formError.value = 'Incorrect email or password. Please double-check your credentials and try again.'
            isValidForm.value = false
            console.log(error.response.data)
          })
    }

    return {
      submit,
      formError,
      isValidForm,
    }
  },
}
</script>

<style scoped>

.form-floating, .btn{
  margin-top: 10px;
}

</style>