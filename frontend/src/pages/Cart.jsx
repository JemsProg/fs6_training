import { useEffect, useState, useCallback } from "react";
import { FaTimes } from "react-icons/fa";
import { authRequest } from "../api/Auth_refresh";
import { BASE_URL } from "../api/base";
import Loading from "../components/Loading";

// This page shows the user's cart, lets them change quantities,
// collects shipping information, and starts the GCash checkout process.
export default function Cart() {
  // cartItems stores the list of products currently inside the user's cart.
  const [cartItems, setCartItems] = useState([]);

  // loading is true while we are still asking the backend for cart data.
  const [loading, setLoading] = useState(false);

  // shipping stores the values typed into the shipping form.
  // Each property name should match what the backend CheckoutSerializer expects.
  const [shipping, setShipping] = useState({
    fullName: "",
    address: "",
    city: "",
    postalCode: "",
    country: "",
  });

  const handleCheckout = async () => {
    try {
      // Send the shipping form data to the backend checkout endpoint.
      // authRequest is used because checkout requires the user to be logged in.
      const res = await authRequest("post", "/checkout/gcash/", shipping);

      // The backend returns a PayMongo checkout link.
      const checkoutUrl = res.data.checkout_url;

      if (checkoutUrl) {
        // Redirect the browser to PayMongo so the user can pay with GCash.
        window.location.href = checkoutUrl;
      }
    } catch (error) {
      console.error("Checkout error:", error);
    }
  };

  const fetchCart = useCallback(async () => {
    // Show the loading screen before starting the request.
    setLoading(true);

    try {
      // Get the logged-in user's cart from the backend.
      const res = await authRequest("get", "/cart/");

      // If the backend returns nothing, use an empty array to avoid errors.
      setCartItems(res.data || []);
    } catch (error) {
      console.error("Error fetching cart:", error);
    } finally {
      // finally always runs, whether the request succeeds or fails.
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // useEffect runs after the component first appears on the screen.
    // Here we load the cart immediately when the page opens.
    fetchCart();
  }, [fetchCart]);

  const handleUpdateQty = async (item, newQty) => {
    // If quantity becomes 0 or below, remove the item from the cart instead.
    if (newQty <= 0) return handleRemove(item.id);

    try {
      // The backend serializer expects product_id and qty.
      const payload = { product_id: item.product.id, qty: newQty };

      // Send the new quantity to the backend.
      const res = await authRequest("put", `/cart/update/${item.id}/`, payload);
      const updated = res.data;

      // Replace only the updated cart item in state.
      // prev is the old cartItems array.
      setCartItems((prev) =>
        prev.map((ci) => (ci.id === updated.id ? updated : ci)),
      );
    } catch (error) {
      console.error("Error updating cart item:", error);
    }
  };

  const handleRemove = async (id) => {
    try {
      // Tell the backend to delete this cart item.
      await authRequest("delete", `/cart/delete/${id}/`);

      // Remove the deleted item from the frontend state too.
      // This updates the page without needing to refresh.
      setCartItems((prev) => prev.filter((ci) => ci.id !== id));
    } catch (error) {
      console.error("Error deleting cart item:", error);
    }
  };

  // reduce loops through all cart items and adds their line totals together.
  // Line total means item quantity times item price.
  const subtotal = cartItems.reduce((acc, item) => {
    // parseFloat converts the price from text/string into a number.
    const price = parseFloat(item.product.product_price || 0);
    return acc + item.qty * price;
  }, 0);

  if (loading) {
    // While data is loading, show the Loading component instead of the cart.
    return <Loading />;
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-6 flex justify-center">
      <div className="w-full max-w-5xl space-y-10">
        {/* Cart item list section */}
        <div className="bg-white shadow-md rounded-md p-8">
          <h2 className="text-2xl font-semibold mb-8">Shopping Cart</h2>

          {/* Show this message only when the cart has no items. */}
          {cartItems.length === 0 && (
            <p className="text-sm">Your cart is empty.</p>
          )}

          {/* map creates one cart item UI for every item in cartItems. */}
          {cartItems.map((item) => {
            // If the image is already a full URL, use it directly.
            // If it is only a backend media path, add BASE_URL first.
            const img = item.product.image
              ? item.product.image.startsWith("http")
                ? item.product.image
                : `${BASE_URL}${item.product.image}`
              : "";

            return (
              <div className="border-b py-6" key={item.id}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-6">
                    <img
                      src={img}
                      alt={item.product.product_name}
                      className="w-24 h-16 object-contain"
                    />

                    <div>
                      <h3 className="font-medium">
                        {item.product.product_name}
                      </h3>

                      <div className="flex items-center gap-3 mt-3 text-sm">
                        <span>Qty:</span>

                        <div className="flex items-center border rounded-md">
                          <button
                            onClick={() => handleUpdateQty(item, item.qty - 1)}
                            className="px-3 py-1 hover:bg-gray-100"
                          >
                            −
                          </button>

                          <span className="px-4 py-1 border-x">{item.qty}</span>

                          <button
                            onClick={() => handleUpdateQty(item, item.qty + 1)}
                            className="px-3 py-1 hover:bg-gray-100"
                          >
                            +
                          </button>
                        </div>
                      </div>

                      <p className="text-sm mt-3">
                        Price: $
                        {parseFloat(item.product.product_price).toFixed(2)}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleRemove(item.id)}
                    className="text-gray-500 hover:text-red-600 transition"
                  >
                    {/* FaTimes is the X icon used for removing an item. */}
                    <FaTimes />
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Shipping form section */}
        <div className="bg-white shadow-md rounded-md p-8">
          <h2 className="text-xl font-semibold mb-6">Shipping Information</h2>

          <div className="grid grid-cols-1 gap-4">
            <input
              type="text"
              placeholder="Full Name"
              value={shipping.fullName}
              onChange={(e) => {
                // Keep the old shipping values, then update only fullName.
                setShipping({ ...shipping, fullName: e.target.value });
              }}
              className="border p-2 rounded"
            />

            <input
              type="text"
              placeholder="Address"
              value={shipping.address}
              onChange={(e) => {
                // e.target.value is whatever the user typed in this input.
                setShipping({ ...shipping, address: e.target.value });
              }}
              className="border p-2 rounded"
            />

            <input
              type="text"
              placeholder="City"
              value={shipping.city}
              onChange={(e) => {
                // The spread operator keeps the other shipping fields unchanged.
                setShipping({ ...shipping, city: e.target.value });
              }}
              className="border p-2 rounded"
            />

            <input
              type="text"
              placeholder="Postal Code"
              value={shipping.postalCode}
              onChange={(e) => {
                // This updates only postalCode inside the shipping object.
                setShipping({ ...shipping, postalCode: e.target.value });
              }}
              className="border p-2 rounded"
            />

            <input
              type="text"
              placeholder="Country"
              value={shipping.country}
              onChange={(e) => {
                // This updates only country inside the shipping object.
                setShipping({ ...shipping, country: e.target.value });
              }}
              className="border p-2 rounded"
            />
          </div>
        </div>

        {/* Order summary section */}
        <div className="bg-white shadow-md rounded-md p-8">
          <h2 className="text-xl font-semibold text-center mb-6">
            Order Summary
          </h2>

          <div className="space-y-4 text-sm">
            <div className="flex justify-between border-b pb-4">
              <span>Sub Total</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>

            <div className="flex justify-between font-semibold">
              <span>Total</span>
              <span>${subtotal.toFixed(2)}</span>
            </div>
          </div>

          <button
            onClick={handleCheckout}
            disabled={cartItems.length === 0}
            className="mt-6 w-full bg-blue-900 text-white py-2 rounded-md hover:bg-blue-800 transition disabled:opacity-50"
          >
            {/* disabled makes the button unclickable when the cart is empty. */}
            Checkout
          </button>
        </div>
      </div>
    </div>
  );
}
