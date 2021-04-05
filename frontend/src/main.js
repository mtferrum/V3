import Vue from 'vue'
import Vuex from 'vuex'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import '@babel/polyfill'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import config from './config.js'

Vue.use(Vuex);

const store = new Vuex.Store({
    state: {
        apiUrl: config.apiUrl + "/",
        imagesUrl: config.imagesUrl + "/",
        currentSection: "blacklist"
    },
    getters: {
        currentSection(state) {
            return state.currentSection
        }
    },
    mutations: {},
    actions: {}
});

Vue.config.productionTip = false;

new Vue({
    vuetify,
    store,
    render: function (h) {
        return h(App)
    }
}).$mount('#app');
