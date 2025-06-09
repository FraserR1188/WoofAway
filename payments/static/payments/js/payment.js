// bookings/static/bookings/js/payment.js

document.addEventListener('DOMContentLoaded', function () {
  // Initialize Stripe
  const stripe = Stripe(window.STRIPE_PUBLIC_KEY);
  const elements = stripe.elements();
  const card = elements.create('card');
  card.mount('#card-element');

  // Real-time validation errors
  card.on('change', ({ error }) => {
    document.getElementById('card-errors').textContent = error
      ? error.message
      : '';
  });

  // Form submission
  const form = document.getElementById('payment-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    document.getElementById('submit').disabled = true;

    const { error, paymentIntent } = await stripe.confirmCardPayment(
      window.STRIPE_CLIENT_SECRET,
      {
        payment_method: {
          card: card,
          billing_details: {
            name: document.getElementById('id_name').value,
            email: document.getElementById('id_email').value,
            address: {
              line1: document.getElementById('id_street_address').value,
              city: document.getElementById('id_city').value,
              postal_code: document.getElementById('id_postcode').value,
              country: document.getElementById('id_country').value,
            },
          },
        },
      }
    );

    if (error) {
      document.getElementById('card-errors').textContent = error.message;
      document.getElementById('submit').disabled = false;
    } else {
      window.location.href = `/bookings/${window.BOOKING_PK}/success/`;
    }
  });
});
