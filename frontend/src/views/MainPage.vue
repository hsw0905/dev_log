<template>
	<div>Main Page</div>
</template>

<script>
import { fetchPosts } from '@/api';

export default {
	name: 'MainPage',
	methods: {
		async fetchData() {
			const response = await fetchPosts();
			console.log(response);
		},
	},
	created() {
		this.fetchData();
	},
};
</script>

<style scoped></style>
