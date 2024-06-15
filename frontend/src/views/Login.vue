<template>
  <main>
    <div class="form mx-auto">

      <LoginForm />

    </div>
  </main>
</template>

<script>
import LoginForm from "@/components/LoginForm";

export default {
  name: "Login",
  components: {LoginForm},
}
</script>

<style scoped>

.form{
  margin-top: 100px;
  width: 100%;
  max-width: 400px;
}

.form-selector a{
  cursor: pointer;
}

</style>
