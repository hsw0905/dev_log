<template>
	<header>
		<div class="wrapper">
			<router-link to="/" class="site-title">HSW.Log</router-link>
			<nav>
				<ol class="nav-menu">
					<router-link to="/books" class="nav-item">Books</router-link>
					<router-link to="/posts" class="nav-item">Posts</router-link>
					<router-link to="/about" class="nav-item">About</router-link>
				</ol>
			</nav>
		</div>
	</header>
</template>

<script>
export default {
	name: 'AppHeader',
};
</script>

<style scoped>
.wrapper {
	max-width: 768px;
	clear: both;
	margin-left: auto;
	margin-right: auto;
	padding: 1em;
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-family: BalsamiqS, -apple-system, BlinkMacSystemFont, 'Nanum Gothic',
		'Roboto', 'Segoe UI', 'Helvetica Neue', 'Lucida Grande', Arial, sans-serif;
	font-size: 1.25em;
	font-weight: bold;
}

.site-title {
	display: flex;
	align-self: center;
	font-weight: bold;
	color: black;
}

.nav-item {
	padding-left: 10px;
	padding-right: 10px;
}

.nav-item:hover {
	color: black;
}
</style>
