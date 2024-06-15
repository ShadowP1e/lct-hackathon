import { createStore } from 'vuex';
import { localStoragePlugin } from '@/store/localStoragePlugin';

const store = createStore({
    state: {
        userIsLoggedIn: false,
    },
    mutations: {
        setUserLoggedIn(state, status) {
            state.userIsLoggedIn = status;
        },
    },
    actions: {
        setUserLoggedIn({ commit }, status) {
            commit('setUserLoggedIn', status);
        },
    },
    getters: {
        userIsLoggedIn: state => state.userIsLoggedIn,
    },
    plugins: [localStoragePlugin]
});

export default store;