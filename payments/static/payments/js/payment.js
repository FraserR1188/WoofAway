// payments/static/payments/js/payment.js

document.addEventListener('DOMContentLoaded', () => {
  // 1) Guard: required globals
  if (
    !window.STRIPE_PUBLIC_KEY ||
    !window.STRIPE_CLIENT_SECRET ||
    !window.BOOKING_PK ||
    !window.PAYMENT_SUCCESS_URL
  ) {
    console.error('Missing Stripe config on window:', {
      public: window.STRIPE_PUBLIC_KEY,
      secret: window.STRIPE_CLIENT_SECRET,
      booking: window.BOOKING_PK,
      success: window.PAYMENT_SUCCESS_URL,
    });
    return;
  }

  // 2) Initialize Stripe + Elements
  const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
  const elements = stripe.elements();
  const style = {
    base: {
      color: '#32325d',
      fontSize: '16px',
      '::placeholder': { color: '#a0aec0' },
    },
  };
  const card = elements.create('card', { style, hidePostalCode: true });
  card.mount('#card-element');

  // 3) Validation errors
  card.on('change', (event) => {
    const display = document.getElementById('card-errors');
    display.textContent = event.error ? event.error.message : '';
  });

  // 4) Handle form submit
  const form = document.getElementById('payment-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit');
    btn.disabled = true;

    // Build a minimal address object:
    const addrLine1 = document
      .getElementById('id_street_address')
      ?.value.trim();
    const city = document.getElementById('id_city')?.value.trim();
    const post = document.getElementById('id_postcode')?.value.trim();
    let country = document.getElementById('id_country')?.value.trim();

    // Default country to GB if blank
    if (!country) {
      country = 'GB';
    }

    // Only include non-empty keys
    const address = {};
    if (addrLine1) address.line1 = addrLine1;
    if (city) address.city = city;
    if (post) address.postal_code = post;
    if (country) address.country = country;

    const billing_details = {
      name: document.getElementById('id_name')?.value.trim() || '',
      email: document.getElementById('id_email')?.value.trim() || '',
      address,
    };

    // Confirm the Card Payment
    const { error, paymentIntent } = await stripe.confirmCardPayment(
      window.STRIPE_CLIENT_SECRET,
      {
        payment_method: {
          card,
          billing_details,
        },
      }
    );

    if (error) {
      document.getElementById('card-errors').textContent = error.message;
      btn.disabled = false;
    } else if (paymentIntent && paymentIntent.status === 'succeeded') {
      // Success!
      window.location.href = `${window.PAYMENT_SUCCESS_URL}?booking_id=${window.BOOKING_PK}`;
    } else {
      document.getElementById('card-errors').textContent =
        'Payment failed. Please try again.';
      btn.disabled = false;
    }
  });
});
