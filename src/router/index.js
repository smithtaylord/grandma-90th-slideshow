import { createRouter, createWebHistory } from 'vue-router'
import SlideshowView from '../views/SlideshowView.vue'
import SyncToolView from '../views/SyncToolView.vue'

const routes = [
  { path: '/', name: 'home', component: SlideshowView },
  { path: '/sync', name: 'sync', component: SyncToolView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})