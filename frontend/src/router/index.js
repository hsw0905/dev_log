import Vue from 'vue';
import VueRouter from 'vue-router';

Vue.use(VueRouter);

const routes = [
	{
		path: '/',
		component: () => import('@/views/MainPage.vue'),
	},
	{
		path: '*',
		component: () => import('@/views/NotFoundPage.vue'),
	},
];

const router = new VueRouter({
	mode: 'history',
	routes,
});

export default router;
