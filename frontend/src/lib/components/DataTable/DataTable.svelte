<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let data: any[][] = [];
  export let headers: string[] = [];
  export let minimized = false;
  
  const dispatch = createEventDispatcher();
  
  function toggleMinimize() {
    dispatch('toggleMinimize');
  }
  
  function downloadCSV() {
    const csvContent = [
      headers.join(','),
      ...data.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  }
</script>

{#if minimized}
  <button 
    class="btn btn-primary fixed top-4 right-4 z-50 flex items-center space-x-2"
    on:click={toggleMinimize}
  >
    <span class="material-icons text-primary">table_chart</span>
    <span class="font-bold">AFFICHER TABLEAU</span>
  </button>
{:else}
  <div class="card fixed top-0 right-0 h-full w-[600px] flex flex-col z-40">
    <div class="card-header flex justify-between items-center">
      <div class="flex items-center space-x-4">
        <h2 class="card-title text-base">VISUALISATION DONNÉES</h2>
        <span class="badge">{data.length} LIGNES</span>
      </div>
      <div class="flex items-center space-x-2">
        <button class="btn btn-primary" on:click={downloadCSV}>
          <span class="material-icons text-primary">download</span>
        </button>
        <button class="btn btn-primary" on:click={toggleMinimize}>
          <span class="material-icons text-primary">close</span>
        </button>
      </div>
    </div>
    
    <div class="card-body flex-1 overflow-auto">
      <table class="table w-full">
        <thead>
          <tr class="bg-primary text-primary-content">
            {#each headers as header}
              <th class="text-left p-3 text-sm font-bold text-primary tracking-wider">{header}</th>
            {/each}
          </tr>
        </thead>
        <tbody>
          {#each data as row}
            <tr class="hover:bg-gray-100">
              {#each row as cell}
                <td class="p-3 text-sm border-r border-gray-200 last:border-r-0">{cell}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}

<style>
  /* No styles needed, using DaisyUI classes */
</style>
