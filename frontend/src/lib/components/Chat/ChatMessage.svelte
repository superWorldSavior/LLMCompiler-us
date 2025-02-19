<script lang="ts">
  import type { ChatMessage } from '$lib/stores/chat';
  import { onMount } from 'svelte';
  
  export let message: ChatMessage;
  
  let messageElement: HTMLDivElement;
  
  onMount(() => {
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth' });
    }
  });
</script>

<div 
  class="message-box relative {message.isUser ? 'ml-12' : 'mr-12'} 
         {message.type === 'thought' ? 'message-thought' : ''} 
         {message.type === 'error' ? 'message-error' : ''}"
  bind:this={messageElement}
>
  <div class="flex flex-col space-y-2">
    {#if !message.isUser && message.icon}
      <span class="text-xl text-primary">{message.icon}</span>
    {/if}
    
    {#if !message.isUser && message.type === 'thought'}
      <div class="flex space-x-1">
        {#each Array(3) as _, i}
          <div class="w-1.5 h-1.5 bg-warning rounded-full animate-pulse" style="animation-delay: {i * 200}ms"></div>
        {/each}
      </div>
    {/if}
    
    {#if message.type === 'error'}
      <div class="flex items-center space-x-2 bg-error/10 p-2 rounded border-l-2 border-error">
        <span class="text-base">⚠️</span>
        <span class="text-error font-medium">Erreur</span>
      </div>
    {/if}
    
    <div class="space-y-1">
      {#if message.type === 'thought'}
        <span class="text-warning font-medium text-sm">Analyse en cours :</span>
      {/if}
      <p class="text-base leading-relaxed">{message.text}</p>
    </div>
  </div>
  
  <div class="absolute right-2 bottom-2 flex flex-col items-end space-y-1">
    <span class="text-xs text-base-content/60">{message.timestamp.toLocaleTimeString()}</span>
    <span class="badge badge-sm">{message.type?.toUpperCase() || 'OK'}</span>
  </div>
</div>

<style>
  .message-box {
    @apply p-4 bg-base-200 rounded-lg shadow-sm transition-all duration-200;
  }

  .message-box:hover {
    @apply shadow-md;
  }

  .message-box.ml-12 {
    @apply border-l-4 border-l-primary;
  }

  .message-box.mr-12 {
    @apply border-r-4 border-r-secondary;
  }

  .message-thought {
    @apply border-warning;
  }

  .message-error {
    @apply border-error;
  }

  @media (max-width: 768px) {
    .message-box {
      @apply mx-0;
    }
  }
</style>
