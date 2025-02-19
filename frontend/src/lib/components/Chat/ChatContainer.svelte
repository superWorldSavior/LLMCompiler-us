<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { ChatService } from '$lib/services/chat';
  import { chatMessages } from '$lib/stores/chat';
  import ChatMessage from './ChatMessage.svelte';
  import ChatInput from './ChatInput.svelte';
  import DataTable from '../DataTable/DataTable.svelte';
  
  let chatService: ChatService;
  let tableMinimized = false;
  let activeTable = null;
  let messagesContainer: HTMLDivElement;

  onMount(() => {
    chatService = new ChatService();
    scrollToBottom();
  });

  onDestroy(() => {
    if (chatService) {
      chatService.disconnect();
    }
  });

  function handleMessage(event: CustomEvent<string>) {
    const message = event.detail;
    chatMessages.addMessage(message, true);
    chatService.sendMessage(message);
  }

  function handleTableClick(table) {
    activeTable = table;
    tableMinimized = false;
  }

  function handleTableMinimize() {
    tableMinimized = !tableMinimized;
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  $: {
    if ($chatMessages) {
      setTimeout(scrollToBottom, 100);
    }
  }

  $: containerClass = tableMinimized 
    ? 'w-full' 
    : activeTable ? 'w-[calc(100%-600px)]' : 'w-full';
</script>

<div class="flex h-screen bg-base-100">
  <div class="flex-1 flex flex-col transition-all duration-300 {containerClass}">
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="bg-base-200 border-b border-base-300 p-4">
        <h1 class="text-xl font-bold text-primary tracking-wider mb-2 flex items-center">
          <span class="material-icons mr-2">chat</span>
          Assistant IA
        </h1>
        <div class="flex flex-wrap gap-2">
          <span class="badge badge-primary">Connecté</span>
          <span class="badge">Latence: 23ms</span>
        </div>
      </div>

      <!-- Messages -->
      <div 
        bind:this={messagesContainer}
        class="flex-1 overflow-y-auto p-4 space-y-4 bg-base-100"
      >
        {#each $chatMessages as message}
          <div class="relative group">
            <ChatMessage {message} />
            {#if message.table}
              <button 
                class="btn btn-ghost btn-sm absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                on:click={() => handleTableClick(message.table)}
              >
                <span class="material-icons text-primary">table_chart</span>
                <span class="ml-1 text-sm">Voir tableau</span>
              </button>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Input -->
      <div class="p-4 bg-base-200 border-t border-base-300">
        <ChatInput on:submit={handleMessage} />
      </div>
    </div>
  </div>

  {#if activeTable}
    <DataTable 
      data={activeTable.rows} 
      headers={activeTable.headers}
      minimized={tableMinimized}
      on:toggleMinimize={handleTableMinimize}
    />
  {/if}
</div>

<svelte:head>
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</svelte:head>
