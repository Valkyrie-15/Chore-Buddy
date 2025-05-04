//store/index.js

import { createStore } from "vuex";
import router from "../router";
import { jwtDecode } from "jwt-decode";
//import axios from "axios";

export default createStore({
  state: {
    token: localStorage.getItem("token") || "",
    user: JSON.parse(localStorage.getItem("user")) || null,
  },
  // store/index.js
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => {
      // First try to get role from user object
      if (state.user && state.user.role) {
        return state.user.role;
      }

      // Fallback to checking JWT token
      if (state.token) {
        try {
          const decoded = jwtDecode(state.token);
          return decoded.role || null;
        } catch (error) {
          console.error("Token decode error:", error);
          return null;
        }
      }
      return null;
    },
  },
  mutations: {
    setToken(state, token) {
      state.token = token;
      if (token) {
        localStorage.setItem("token", token);
      } else {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    },
    setUser(state, user) {
      state.user = user;
      if (user) {
        localStorage.setItem("user", JSON.stringify(user));
      } else {
        localStorage.removeItem("user");
      }
    },
    userRole: (state) => {
      if (state.token) {
        try {
          const decoded = jwtDecode(state.token);
          console.log("Decoded token:", decoded); // Add this debug line
          return decoded.role || null;
        } catch (error) {
          console.error("Token decode error:", error); // Add this debug line
          return null;
        }
      }
      return null;
    },
    logout(state) {
      state.token = "";
      state.user = null;
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    },
  },
  actions: {
    login({ commit }, { token, user }) {
      commit("setToken", token);
      commit("setUser", user);
    },
    logout({ commit }) {
      commit("logout");
      router.push("/login"); // Ensure the router redirects to login
    },
  },
});
