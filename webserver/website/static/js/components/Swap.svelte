<script>
    import { connected, account } from '../stores/auth.js';
    import { availableTokens, fetchAvailableTokens } from '../stores/crypto.js';
    import { onMount, onDestroy } from 'svelte';
    import Buy from './Buy.svelte';
    
    let inputAmount = '';
    let outputAmount = '';
    let selectedInputToken = {
        id: "3408",  // USDC's ID
        symbol: "USDC",
        name: "USD Coin",
        logo: "https://s2.coinmarketcap.com/static/img/coins/64x64/3408.png",
        price: 1.0
    };
    const CABL_TOKEN = {
        id: "cabl",
        symbol: "CABL",
        name: "Cable Token",
        logo: "/static/images/cabl-logo.png",
        price: 1
    };
    let selectedOutputToken = CABL_TOKEN;
    let showInputDropdown = false;
    let showOutputDropdown = false;
    let searchQuery = '';
    let activeTab = 'swap';
    
    // Fee calculations
    const PRICE_IMPACT = 0.0087; // 0.87%
    let networkFee = 1.5; // Default value until we fetch the real fee

    let transactionDetails = null;

    let pollingInterval;

    // Add missing variables
    let showBreakdown = true;  // Controls transaction breakdown visibility
    
    // Add computed values for the breakdown display
    $: ({
        estimatedAmount: estimatedCABL = '0.000',
        minimumAmount: minimumReceived = '0.000',
        networkFeeUSD = '0.000',
    } = transactionDetails || {});

    // Toggle function for breakdown
    function toggleBreakdown() {
        showBreakdown = !showBreakdown;
    }

    // Function to start polling
    function startPolling() {
        // Initial fetch
        fetchAvailableTokens();
        
        // Set up interval for subsequent fetches
        pollingInterval = setInterval(async () => {
            console.log('Refreshing cryptocurrency data...');
            await fetchAvailableTokens();
        }, 60000); // 60 seconds
    }

    // Add fee constant
    const SWAP_FEE_PERCENT = 0.0025; // 0.25%

    // Update fetchTransactionDetails to include swap fee
    async function fetchTransactionDetails(currency, amount) {
        try {
            const exactInputValue = parseFloat(amount);
            const inputValueInUSD = exactInputValue * selectedInputToken.price;
            
            // Log input state
            console.log('Input values:', {
                exactInputValue,
                inputValueInUSD,
                tokenPrice: selectedInputToken.price
            });
            
            // Fetch network fee from API
            const response = await fetch(`/api/crypto/transaction-details/${currency}/${amount}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            // Convert network fee from ETH to USD if not USDC
            const networkFeeUSD = data.networkFee * selectedInputToken.price;
            
            // Calculate swap fee in USD
            const swapFeeUSD = inputValueInUSD * SWAP_FEE_PERCENT;
            
            // Calculate available amount in USD
            const availableInUSD = inputValueInUSD - networkFeeUSD - swapFeeUSD;
            
            // Convert to CABL tokens
            const estimatedAmount = availableInUSD / CABL_TOKEN.price;
            
            // Convert fees back to input token for display
            const networkFeeInToken = networkFeeUSD / selectedInputToken.price;
            const swapFeeInToken = swapFeeUSD / selectedInputToken.price;

            return {
                inputAmount: exactInputValue,
                inputAmountUSD: inputValueInUSD,
                networkFee: networkFeeInToken,
                networkFeeUSD: networkFeeUSD,
                swapFee: swapFeeInToken,
                swapFeeUSD: swapFeeUSD,
                availableForSwap: availableInUSD,
                estimatedAmount,
                minimumAmount: estimatedAmount * 0.995, // 0.5% slippage
                pricePerToken: CABL_TOKEN.price,
                totalCost: exactInputValue
            };
        } catch (error) {
            console.error('Error calculating transaction details:', error);
            return null;
        }
    }

    // Update transaction details calculation
    async function updateTransactionDetails() {
        if (inputAmount && selectedInputToken) {
            const details = await fetchTransactionDetails(selectedInputToken.symbol, inputAmount);
            
            if (details) {
                transactionDetails = details;
                estimatedCABL = details.estimatedAmount.toFixed(3);
                minimumReceived = (details.estimatedAmount * 0.995).toFixed(3);
                networkFeeUSD = parseFloat(details.networkFeeUSD).toFixed(3);
                swapFeeUSD = details.swapFee?.toFixed(3) || '0.000';
            }
        } else {
            transactionDetails = null;
            estimatedCABL = '0.000';
            minimumReceived = '0.000';
            networkFeeUSD = '0.000';
            swapFeeUSD = '0.000';
        }
    }

    // Fix input validation and calculations
    function handleInput(event) {
        const value = event.target.value;
        
        // Remove any non-numeric characters except decimal point
        const sanitizedValue = value.replace(/[^\d.]/g, '');
        
        // Ensure only one decimal point
        const parts = sanitizedValue.split('.');
        if (parts.length > 2) {
            event.target.value = inputAmount;
            return;
        }
        
        // Update only if it's a valid number or empty
        if (sanitizedValue === '' || /^\d*\.?\d*$/.test(sanitizedValue)) {
            inputAmount = sanitizedValue;
            
            if (sanitizedValue && selectedInputToken) {
                const exactInputValue = parseFloat(sanitizedValue);
                // Convert input token value to USD first, then to CABL
                const inputValueInUSD = exactInputValue * selectedInputToken.price;
                const availableForSwap = inputValueInUSD - networkFee;
                
                if (availableForSwap > 0) {
                    outputAmount = (availableForSwap / CABL_TOKEN.price).toFixed(3);
                } else {
                    outputAmount = '0';
                }
                
                updateTransactionDetails();
            } else {
                outputAmount = '';
                transactionDetails = null;
            }
        } else {
            event.target.value = inputAmount;
        }
    }

    // Update the USD value display
    $: displayInputUsdValue = inputAmount && selectedInputToken 
        ? (parseFloat(inputAmount) * selectedInputToken.price).toFixed(2) 
        : '0.00';

    // Initialize computed values
    let estimatedCABL = '0.000';
    let minimumReceived = '0.000';
    let networkFeeUSD = '0.000';

    // Update onMount
    onMount(async () => {
        startPolling();
        await updateTransactionDetails();
    });

    // Clean up interval when component is destroyed
    onDestroy(() => {
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
    });

    onMount(async () => {
        await fetchAvailableTokens();
        console.log('Available tokens:', $availableTokens); // Debug log
    });

    function handleImageError(event) {
        event.target.src = '/static/images/default-token.png';
    }

    function selectInputToken(token) {
        selectedInputToken = token;
        showInputDropdown = false;
        searchQuery = '';
        
        // Recalculate output amount with new token
        if (inputAmount) {
            const exactInputValue = parseFloat(inputAmount);
            const inputValueInUSD = exactInputValue * token.price;
            const availableForSwap = inputValueInUSD - networkFee;
            
            if (availableForSwap > 0) {
                outputAmount = (availableForSwap / CABL_TOKEN.price).toFixed(3);
            } else {
                outputAmount = '0';
            }
        }
        
        // Update transaction details
        updateTransactionDetails();
        
        console.log('Selected input token:', token); // Debug log
    }

    function selectOutputToken(token) {
        selectedOutputToken = token;
        showOutputDropdown = false;
        searchQuery = '';
        console.log('Selected output token:', token); // Debug log

        updateTransactionDetails
    }

    function handleSwap() {
        if (!$connected) {
            alert('Please connect your wallet first');
            return;
        }
        console.log('Swapping...');
    }

    $: filteredTokens = searchQuery 
        ? $availableTokens.filter(token => 
            token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            token.symbol.toLowerCase().includes(searchQuery.toLowerCase())
          )
        : $availableTokens;

    $: console.log('Dropdown state:', { showInputDropdown, showOutputDropdown }); // Debug log

    // Update computed values
    // $: displayInputUsdValue = inputAmount ? parseFloat(inputAmount).toFixed(2) : '0.00';
    
    // USD value under Buy amount should reflect CABL token value
    $: displayOutputUsdValue = outputAmount 
        ? (parseFloat(outputAmount) * CABL_TOKEN.price).toFixed(2) 
        : '0.00';
    
    // Add reactive statement for formatted details
    $: formattedTransactionDetails = transactionDetails ? {
        estimatedAmount: transactionDetails.estimatedAmount.toFixed(3),
        minimumReceived: transactionDetails.minimumAmount.toFixed(3),
        networkFee: `$${parseFloat(transactionDetails.networkFeeUSD).toFixed(3)}`,
        pricePerToken: `$${CABL_TOKEN.price.toFixed(3)}`,
        totalCost: `${transactionDetails.totalCost.toFixed(6)} ${selectedInputToken.symbol}`
    } : {
        estimatedAmount: '0.000',
        minimumReceived: '0.000',
        networkFee: '$0.000',
        pricePerToken: `$${CABL_TOKEN.price.toFixed(3)}`,
        totalCost: `0.000000 ${selectedInputToken?.symbol || 'USDC'}`
    };

    // Add computed values for fees
    $: swapFeeUSD = transactionDetails?.swapFee?.toFixed(3) || '0.000';
</script>

{#if activeTab === 'swap'}
    <div class="swap-container">
        <div class="swap-card">
            <!-- Tab Navigation -->
            <div class="tab-navigation">
                <button 
                    class="tab-button" 
                    class:active={activeTab === 'swap'}
                    on:click={() => activeTab = 'swap'}
                >
                    Swap
                </button>
                <button 
                    class="tab-button" 
                    class:active={activeTab === 'buy'}
                    on:click={() => activeTab = 'buy'}
                >
                    Buy
                </button>
            </div>

            <!-- Input Section -->
            <div class="section">
                <span class="label">Sell</span>
                <div class="amount-input">
                    <input 
                        type="text"
                        bind:value={inputAmount}
                        placeholder="0.0"
                        on:input={handleInput}
                    />
                    <button 
                        class="token-selector"
                        on:click={() => {
                            showInputDropdown = !showInputDropdown;
                            showOutputDropdown = false;  // Close other dropdown
                            console.log('Toggling input dropdown');  // Debug log
                        }}
                    >
                        {#if selectedInputToken}
                            <img 
                                src={selectedInputToken.logo} 
                                alt={selectedInputToken.symbol}
                                on:error={handleImageError}
                            />
                            <span>{selectedInputToken.symbol}</span>
                        {:else}
                            <img 
                                src="https://raw.githubusercontent.com/Uniswap/interface/main/src/assets/images/ethereum-logo.png" 
                                alt="ETH"
                                on:error={handleImageError}
                            />
                            <span>ETH</span>
                        {/if}
                        <span class="chevron">▼</span>
                    </button>
                </div>
                <div class="balance">
                    <span class="balance-amount">$ {displayInputUsdValue}</span>
                </div>
            </div>

            <!-- Swap Icon -->
            <div class="swap-icon">
                <button class="swap-direction">↓</button>
            </div>

            <!-- Output Section -->
            <div class="section">
                <span class="label">Buy</span>
                <div class="amount-input">
                    <input 
                        type="text"
                        readonly
                        value={outputAmount}
                        placeholder="0.0"
                    />
                    <button 
                        class="token-selector"
                        disabled
                    >
                        {#if selectedOutputToken.logo.startsWith('http')}
                            <img src={selectedOutputToken.logo} alt={selectedOutputToken.symbol} />
                        {:else if selectedOutputToken.logo.startsWith('/')}
                            <img src={selectedOutputToken.logo} alt={selectedOutputToken.symbol} />
                        {:else}
                            <span class="token-emoji">{selectedOutputToken.symbol}</span>
                        {/if}
                        <span>{selectedOutputToken.symbol}</span>
                    </button>
                </div>
                <div class="balance">
                    <span class="balance-amount">$ {displayOutputUsdValue}</span>
                </div>
            </div>

            {#if $connected}
                <button 
                    class="swap-button" 
                    disabled={!inputAmount || parseFloat(inputAmount) <= 0}
                    on:click={handleSwap}
                >
                    Swap
                </button>
            {:else}
                <button 
                    class="connect-button"
                    on:click={() => window.ethereum.request({ method: 'eth_requestAccounts' })}
                >
                    Connect Wallet
                </button>
            {/if}

            <!-- Update the button to toggle breakdown -->
            <button 
                class="breakdown-toggle" 
                on:click={toggleBreakdown}
            >
                {showBreakdown ? 'Hide' : 'Show'} details ↓
            </button>

            {#if showBreakdown}
                <div class="transaction-breakdown">
                    <div class="breakdown-item">
                        <span>Est. received</span>
                        <span class="value">{estimatedCABL} CABL</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Min. received</span>
                        <span class="value">{minimumReceived} CABL</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Network fee</span>
                        <span class="value">${parseFloat(networkFeeUSD).toFixed(3)}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Swap fee (0.25%)</span>
                        <span class="value">${swapFeeUSD}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Price per token</span>
                        <span class="value">${CABL_TOKEN.price}</span>
                    </div>
                </div>
            {/if}
        </div>
    </div>
{:else}
    <Buy />
{/if}

{#if showInputDropdown || showOutputDropdown}
    <div class="token-modal-overlay">
        <div class="token-modal">
            <div class="modal-header">
                <h3>Select a token</h3>
                <button class="close-button" on:click={() => {
                    showInputDropdown = false;
                    showOutputDropdown = false;
                    searchQuery = '';
                }}>×</button>
            </div>
            
            <div class="search-box">
                <input 
                    type="text" 
                    bind:value={searchQuery}
                    placeholder="Search name or paste address"
                />
            </div>

            <div class="token-list">
                {#each filteredTokens as token}
                    <button 
                        class="token-option"
                        on:click={() => {
                            if (showInputDropdown) selectInputToken(token);
                            if (showOutputDropdown) selectOutputToken(token);
                        }}
                    >
                        <div class="token-info">
                            <img 
                                src={token.logo} 
                                alt={token.symbol}
                                on:error={handleImageError}
                            />
                            <div class="token-details">
                                <span class="token-symbol">{token.symbol}</span>
                                <span class="token-name">{token.name}</span>
                            </div>
                        </div>
                    </button>
                {/each}
            </div>
        </div>
    </div>
{/if}

<style>
    .swap-container {
        max-width: 480px;
        margin: 20px auto;
        padding: 0 16px;
    }

    .swap-card {
        background: rgb(13, 17, 28);
        border-radius: 16px;
        padding: 12px;
    }

    .tab-navigation {
        display: flex;
        margin-bottom: 12px;
        background: rgb(19, 26, 42);
        border-radius: 12px;
        padding: 2px;
    }

    .tab-button {
        flex: 1;
        padding: 8px;
        color: #5d6785;
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 16px;
        border-radius: 12px;
        transition: all 0.2s;
    }

    .tab-button.active {
        color: white;
        background: rgb(41, 50, 73);
    }

    .section {
        background: rgb(19, 26, 42);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 2px;
    }

    .label {
        color: rgb(152, 161, 192);
        font-size: 14px;
        margin-bottom: 8px;
        display: block;
    }

    .amount-input {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }

    input {
        background: transparent;
        border: none;
        color: white;
        font-size: 28px;
        width: 100%;
        outline: none;
        padding: 0;
    }

    input::placeholder {
        color: rgb(152, 161, 192);
    }

    .token-selector {
        display: flex;
        align-items: center;
        padding: 4px 8px 4px 4px;
        background: rgb(41, 50, 73);
        border: none;
        border-radius: 20px;
        color: white;
        cursor: pointer;
        font-size: 16px;
        min-width: 100px;
    }

    .token-selector img {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .token-selector .chevron {
        margin-left: 4px;
    }

    .chevron {
        color: rgb(152, 161, 192);
        font-size: 12px;
    }

    .balance {
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
    }

    .balance-amount {
        color: rgb(152, 161, 192);
        font-size: 14px;
    }

    .swap-icon {
        display: flex;
        justify-content: center;
        margin: -8px 0;
        position: relative;
        z-index: 2;
    }

    .swap-direction {
        width: 32px;
        height: 32px;
        background: rgb(19, 26, 42);
        border: 4px solid rgb(13, 17, 28);
        border-radius: 8px;
        color: rgb(152, 161, 192);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .swap-direction:hover {
        background: rgb(41, 50, 73);
        color: white;
    }
/* 
    .connect-wallet-button {
        width: 100%;
        padding: 16px;
        margin-top: 12px;
        background: rgb(76, 130, 251);
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }

    .connect-wallet-button:hover {
        background: rgb(99, 145, 255);
    } */

    .token-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(13, 17, 28, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }

    .token-modal {
        background: rgb(13, 17, 28);
        border: 1px solid rgb(41, 50, 73);
        border-radius: 20px;
        width: 100%;
        max-width: 420px;
        max-height: 80vh;
        margin: 16px;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid rgb(41, 50, 73);
    }

    .modal-header h3 {
        color: white;
        margin: 0;
        font-size: 16px;
    }

    .close-button {
        background: none;
        border: none;
        color: rgb(152, 161, 192);
        font-size: 24px;
        cursor: pointer;
        padding: 4px;
    }

    .close-button:hover {
        color: white;
    }

    .search-box {
        padding: 16px;
        border-bottom: 1px solid rgb(41, 50, 73);
    }

    .search-box input {
        width: 100%;
        padding: 12px;
        background: rgb(19, 26, 42);
        border: none;
        border-radius: 12px;
        color: white;
        font-size: 16px;
    }

    .token-list {
        padding: 8px;
        overflow-y: auto;
        max-height: 300px;
    }

    .token-option {
        width: 100%;
        padding: 8px 12px;
        background: transparent;
        border: none;
        color: white;
        display: flex;
        align-items: center;
        cursor: pointer;
        border-radius: 12px;
        text-align: left;
    }

    .token-option:hover {
        background: rgb(41, 50, 73);
    }

    .token-info {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
    }

    .token-info img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }

    .token-details {
        display: flex;
        flex-direction: column;
    }

    .token-symbol {
        font-weight: 500;
        font-size: 16px;
    }

    .token-name {
        color: rgb(152, 161, 192);
        font-size: 12px;
    }

    .transaction-breakdown {
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid rgb(41, 50, 73);
    }

    .breakdown-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: rgb(152, 161, 192);
        font-size: 14px;
        padding: 4px 0;
    }

    .value {
        color: white;
    }

    /* Make output input look disabled */
    input[readonly] {
        cursor: not-allowed;
        opacity: 0.7;
    }

    .token-selector[disabled] {
        cursor: not-allowed;
        opacity: 0.7;
    }

    /* Add style for breakdown toggle if needed */
    .breakdown-toggle {
        width: 100%;
        padding: 8px;
        background: transparent;
        border: none;
        color: rgb(152, 161, 192);
        cursor: pointer;
        font-size: 14px;
    }

    .breakdown-toggle:hover {
        color: white;
    }

    /* Add style for token emoji fallback */
    .token-emoji {
        font-size: 24px;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Add styles for the buttons */
    .swap-button, .connect-button {
        width: 100%;
        padding: 16px;
        border-radius: 12px;
        border: none;
        background: rgb(76, 130, 251);
        color: white;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 16px;
    }

    .swap-button:disabled {
        background: rgba(76, 130, 251, 0.5);
        cursor: not-allowed;
    }

    .swap-button:hover:not(:disabled) {
        background: rgb(56, 110, 231);
    }
</style> 