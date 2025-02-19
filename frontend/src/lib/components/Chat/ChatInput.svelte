<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  let message = '';

  function handleSubmit() {
    if (message.trim()) {
      dispatch('submit', message);
      message = '';
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="flex flex-col space-y-2">
  <div class="flex justify-between">
    <div class="flex items-center space-x-2">
      <span class="material-icons text-primary text-sm">edit</span>
      <span class="text-sm text-base-content/70">Message</span>
    </div>
    <div class="flex items-center space-x-2">
      <span class="material-icons text-primary text-sm">circle</span>
      <span class="text-sm text-base-content/70">En ligne</span>
    </div>
  </div>

  <div class="flex gap-4">
    <div class="flex-1">
      <textarea
        bind:value={message}
        on:keydown={handleKeydown}
        placeholder="Entrez votre message..."
        rows="1"
        class="textarea textarea-bordered w-full min-h-[40px] resize-none bg-base-100 
               focus:border-primary placeholder-base-content/30"
      ></textarea>
    </div>
    
    <button 
      on:click={handleSubmit} 
      disabled={!message.trim()}
      class="btn btn-primary min-w-[100px]"
    >
      <span class="material-icons text-sm mr-1">send</span>
      Envoyer
    </button>
  </div>
</div>

<style>
  /* Les styles sont maintenant gérés par les classes Tailwind et les composants dans app.css */
</style>
