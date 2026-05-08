import axios from "axios";
import { BASE_URL } from "./base";

// authRequest is a reusable helper for API calls that need login.
// Instead of writing axios and Authorization headers in every page,
// we call authRequest("get", "/cart/") or authRequest("post", "/checkout/gcash/", data).
export const authRequest = async (method, url, data = null) => {
  try {
    // First attempt: send the request using the current access token.
    // The access token proves to the backend that the user is logged in.
    return await axios({
      method,
      // BASE_URL is the backend server, and url is the endpoint path.
      url: `${BASE_URL}${url}`,
      // data is the request body. It is usually used for POST and PUT requests.
      data,
      headers: {
        // Django REST Framework expects JWT tokens in this format:
        // Authorization: Bearer your_access_token_here
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });
  } catch (error) {
    // If the error is not 401, it is not an expired-token problem.
    // So we throw the error back to the page that called authRequest.
    if (error.response?.status !== 401) throw error;

    // A 401 usually means the access token expired.
    // Use the refresh token to ask the backend for a new access token.
    const refreshResponse = await axios.post(`${BASE_URL}/api/token/refresh/`, {
      refresh: localStorage.getItem("refresh_token"),
    });

    // Save the new access token so future requests can use it.
    const newAccess = refreshResponse.data.access;
    localStorage.setItem("access_token", newAccess);

    // Retry the original request, but this time use the new access token.
    // This makes the page continue working without forcing the user to log in again.
    return axios({
      method,
      url: `${BASE_URL}${url}`,
      data,
      headers: {
        Authorization: `Bearer ${newAccess}`,
      },
    });
  }
};
