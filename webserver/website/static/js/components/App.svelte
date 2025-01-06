<script>
    import Swap from './Swap.svelte';
    import { connected, account, provider as providerStore, signer as signerStore } from '../stores/auth.js';
    import { onMount } from 'svelte';
    import { ethers } from 'ethers';
    let currentView = 'swap';

    // Add debug logging
    $: console.log('Wallet state in App:', { 
        connected: $connected, 
        account: $account,
        hasProvider: !!$providerStore
    });

    onMount(async () => {
        if (window.ethereum) {
            // Check if already connected
            const accounts = await window.ethereum.request({ method: 'eth_accounts' });
            if (accounts.length > 0) {
                const provider = new ethers.BrowserProvider(window.ethereum);
                const signer = await provider.getSigner();
                
                $connected = true;
                $account = accounts[0];
                $providerStore = provider;
                $signerStore = signer;
            }

            // Listen for account changes
            window.ethereum.on('accountsChanged', async function (accounts) {
                if (accounts.length === 0) {
                    $connected = false;
                    $account = null;
                    $providerStore = null;
                    $signerStore = null;
                } else {
                    const provider = new ethers.BrowserProvider(window.ethereum);
                    const signer = await provider.getSigner();
                    
                    $connected = true;
                    $account = accounts[0];
                    $providerStore = provider;
                    $signerStore = signer;
                }
            });
        }
    });

    async function connectWallet() {
        if (typeof window.ethereum !== 'undefined') {
            try {
                const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
                $connected = true;
                $account = accounts[0];
                
                // Initialize provider and signer
                const provider = new ethers.BrowserProvider(window.ethereum);
                const signer = await provider.getSigner();
                
                $providerStore = provider;
                $signerStore = signer;
            } catch (error) {
                console.error('User denied account access');
            }
        } else {
            alert('Please install MetaMask!');
        }
    }
</script>

<style>
    main {
        background: linear-gradient(180deg, #0d1b3e 0%, #000000 150%);
        min-height: 100vh;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .background-effects {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 0;
        overflow: hidden;
    }

    .gradient-sphere {
        position: absolute;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.15;
    }

    .gradient-1 {
        background: radial-gradient(circle at center, #1a4b8c 0%, transparent 70%);
        width: 70vh;
        height: 70vh;
        top: -20vh;
        left: -10vh;
        animation: float 20s ease-in-out infinite;
    }

    .gradient-2 {
        background: radial-gradient(circle at center, #102954 0%, transparent 70%);
        width: 80vh;
        height: 80vh;
        top: 30vh;
        right: -20vh;
        animation: float 25s ease-in-out infinite reverse;
    }

    .gradient-3 {
        background: radial-gradient(circle at center, #1e3c6e 0%, transparent 70%);
        width: 60vh;
        height: 60vh;
        bottom: -20vh;
        left: 30vw;
        animation: float 22s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translate(0, 0); }
        25% { transform: translate(-2%, 2%); }
        50% { transform: translate(2%, -2%); }
        75% { transform: translate(-1%, -1%); }
        100% { transform: translate(0, 0); }
    }

    .content {
        position: relative;
        z-index: 1;
    }

    .nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(13, 27, 62, 0.7);
        backdrop-filter: blur(12px);
    }

    .nav-left, .nav-right {
        display: flex;
        align-items: center;
        gap: 2rem;
    }

    .logo {
        font-size: 24px;
        text-decoration: none;
    }

    .network {
        color: #5d6785;
    }

    button {
        background: none;
        border: none;
        color: #5d6785;
        cursor: pointer;
        padding: 8px 12px;
        font-size: 16px;
    }

    button.active {
        color: white;
    }

    .connect-button {
        background: #4c82fb;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        transition: all 0.2s;
    }

    .connect-button:hover {
        background: #5d8eff;
        transform: translateY(-1px);
    }
</style>

<main>
    <div class="background-effects">
        <div class="gradient-sphere gradient-1"></div>
        <div class="gradient-sphere gradient-2"></div>
        <div class="gradient-sphere gradient-3"></div>
    </div>
    
    <div class="content">
        <nav class="nav">
            <div class="nav-left">
                <a href="/" class="logo">🌊</a>
                <button 
                    class:active={currentView === 'swap'}
                    on:click={() => currentView = 'swap'}
                >
                    Swap
                </button>
                <button 
                    class:active={currentView === 'tokens'}
                    on:click={() => currentView = 'tokens'}
                >
                    Tokens
                </button>
            </div>
            <div class="nav-right">
                <span class="network">Ethereum</span>
                <button class="connect-button" on:click={connectWallet}>
                    {$connected ? $account.slice(0, 6) + '...' + $account.slice(-4) : 'Connect'}
                </button>
            </div>
        </nav>

        {#if currentView === 'swap'}
            <Swap />
        {/if}
    </div>
</main>

