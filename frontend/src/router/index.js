import {createRouter, createWebHistory} from 'vue-router'
import Login from '@/views/Login.vue';
import Video from "@/views/Video";
import CopyrightChecking from "@/views/CopyrightChecking";
import UploadCopyrightVideo from "@/views/UploadCopyrightVideo";
import CopyrightVideo from "@/views/CopyrightVideo";
import Videos from "@/views/Videos";
import CopyrightVideos from "@/views/CopyrightVideos";

const routes = [
    {path: '/login', component: Login},
    {path: '/video/:id', component: Video},
    {path: '/videos', component: Videos},
    {path: '/copyright-videos', component: CopyrightVideos},
    {path: '', component: CopyrightChecking},
    {path: '/upload-copyright-video', component: UploadCopyrightVideo},
    {path: '/copyright-video/:id', component: CopyrightVideo},
]

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
