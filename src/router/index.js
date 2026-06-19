import { createRouter, createWebHistory } from 'vue-router'
import SlideshowView from '../views/SlideshowView.vue'
import SyncToolView from '../views/SyncToolView.vue'
import ReorderView from '../views/ReorderView.vue'

const routes = [
  { path: '/', name: 'home', component: SlideshowView },
  { path: '/sync', name: 'sync', component: SyncToolView },
  { path: '/reorder', name: 'reorder', component: ReorderView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})