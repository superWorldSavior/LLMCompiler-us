<script lang="ts">
  import ChatContainer from '$lib/components/Chat/ChatContainer.svelte';
</script>

<div class="page">
  <main>
    <ChatContainer />
  </main>
</div>

<style>
  .page {
    @apply min-h-screen bg-base-100;
  }

  main {
    @apply flex-1;
  }
</style>
