<script>
    import { connected, account } from '../stores/auth.js';
    
    let amount = '';
    let displayUsdValue = '0.00';
    let showBreakdown = true;
    const CABL_TOKEN = {
        id: "cabl",
        symbol: "CABL",
        name: "Cable Token",
        logo: "/static/images/cabl-logo.png",
        price: 0.1
    };

    // Network fee and calculations
    const STRIPE_FEE_PERCENT = 0.029; // 2.9%
    const STRIPE_FIXED_FEE = 0.30; // $0.30
    let networkFee = 1.5;

    // Computed values
    $: {
        const inputValue = parseFloat(amount) || 0;
        displayUsdValue = (inputValue * CABL_TOKEN.price).toFixed(2);
    }

    // Calculate fees and totals
    $: stripeFee = amount ? (parseFloat(amount) * STRIPE_FEE_PERCENT + STRIPE_FIXED_FEE).toFixed(3) : '0.000';
    $: totalCost = amount ? (parseFloat(amount) + parseFloat(stripeFee) + networkFee).toFixed(3) : '0.000';
    $: estimatedCABL = amount ? (parseFloat(amount) / CABL_TOKEN.price).toFixed(3) : '0.000';

    async function handleBuy() {
        if (!amount) return;
        
        try {
            const response = await fetch('/api/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: parseFloat(amount) * 100, // Convert to cents
                    currency: 'usd',
                    token: 'CABL'
                })
            });

            const session = await response.json();
            // Redirect to Stripe Checkout
            window.location.href = session.url;
        } catch (error) {
            console.error('Error creating checkout session:', error);
            alert('Failed to initiate payment. Please try again.');
        }
    }

    function toggleBreakdown() {
        showBreakdown = !showBreakdown;
    }

    // Input validation for Buy
    function handleInput(event) {
        const value = event.target.value;
        if (!/^\d*\.?\d*$/.test(value)) {
            event.target.value = amount;
            return;
        }
        amount = value;
    }
</script>

<div class="swap-container">
    <div class="swap-card">
        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <button 
                class="tab-button"
                on:click={() => window.location.href = '/swap'}
            >
                Swap
            </button>
            <button 
                class="tab-button active"
            >
                Buy
            </button>
        </div>

        <!-- Amount Input Section -->
        <div class="section">
            <span class="label">Amount</span>
            <div class="amount-input">
                <input 
                    type="text"
                    bind:value={amount}
                    placeholder="0.0"
                    on:input={handleInput}
                    min="0"
                    step="any"
                />
                <button class="token-selector" disabled>
                    <img src={CABL_TOKEN.logo} alt="CABL" />
                    <span>CABL</span>
                </button>
            </div>
            <div class="balance">
                <span class="balance-amount">$ {displayUsdValue}</span>
            </div>
        </div>

        <button 
            class="swap-button"
            disabled={!amount || parseFloat(amount) <= 0}
            on:click={handleBuy}
        >
            Buy CABL
        </button>

        <!-- Breakdown Toggle -->
        <button 
            class="breakdown-toggle" 
            on:click={toggleBreakdown}
        >
            {showBreakdown ? 'Hide' : 'Show'} details ↓
        </button>

        <!-- Transaction Details -->
        {#if showBreakdown}
            <div class="transaction-breakdown">
                <div class="breakdown-item">
                    <span>Est. received</span>
                    <span class="value">{estimatedCABL} CABL</span>
                </div>
                <div class="breakdown-item">
                    <span>Network fee</span>
                    <span class="value">${networkFee.toFixed(3)}</span>
                </div>
                <div class="breakdown-item">
                    <span>Stripe fee (2.9% + $0.30)</span>
                    <span class="value">${stripeFee}</span>
                </div>
                <div class="breakdown-item">
                    <span>Total Cost</span>
                    <span class="value">${totalCost}</span>
                </div>
                <div class="breakdown-item">
                    <span>Price per token</span>
                    <span class="value">${CABL_TOKEN.price}</span>
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    /* Inherit all styles from Swap.svelte */
    .swap-container {
        max-width: 480px;
        margin: 20px auto;
        padding: 0 16px;
    }

    /* ... (copy all other styles from Swap.svelte) ... */
</style> 