import { createRouter, createWebHistory } from "vue-router";
import store from "../store";

import SignupUser from "../auth/SignupUser.vue";
import LoginUser from "../auth/LoginUser.vue";
import AdminDash from "../views/AdminDash.vue";
import AdminServices from "../views/AdminServices.vue";
import AdminUsers from "../views/AdminUsers.vue";
import CustDash from "@/views/CustDash.vue";
import CustBooking from "@/views/CustBooking.vue";
import BookService from "@/views/BookService.vue";
import ProDash from "@/views/ProDash.vue";
import ProJob from "@/views/ProJob.vue";
import ProEarning from "@/views/ProEarning.vue";
import ProReview from "@/views/ProReview.vue";
import AdminReports from "@/views/AdminReports.vue";
import AdminProfile from "@/views/AdminProfile.vue";
import CustProfile from "@/views/CustProfile.vue";
import ProProfile from "@/views/ProProfile.vue";
import HelloWorld from "@/components/HelloWorld.vue";

const routes = [
  {
    path: "/",
    name: "HelloWorld",
    component: HelloWorld,
  },
  {
    path: "/login",
    name: "login",
    component: LoginUser,
  },
  {
    path: "/signup",
    name: "Signup",
    component: SignupUser,
  },
  {
    path: "/admin-dashboard",
    name: "AdminDashboard",
    component: AdminDash,
    meta: { requiresAuth: true },
  },
  {
    path: "/logout",
    name: "Logout",
    beforeEnter: (to, from, next) => {
      store.dispatch("logout").then(() => {
        next("/login");
      });
    },
  },
  {
    path: "/services",
    name: "adminServices",
    component: AdminServices,
    meta: { requiresAuth: true, adminOnly: true },
  },
  {
    path: "/admin-users",
    name: "adminUsers",
    component: AdminUsers,
    meta: { requiresAuth: true, adminOnly: true },
  },
  {
    path: "/cust-dashboard",
    name: "CustDash",
    props: true,
    component: CustDash,
  },
  {
    path: "/my-bookings",
    name: "CustBooking",
    component: CustBooking,
  },
  {
    path: "/book-service",
    name: "BookService",
    component: BookService,
  },
  {
    path: "/pro-dashboard",
    name: "ProDash",
    component: ProDash,
  },
  {
    path: "/my-jobs",
    name: "ProJob",
    component: ProJob,
  },
  {
    path: "/earnings",
    name: "ProEarning",
    component: ProEarning,
  },
  {
    path: "/professional/:id/reviews",
    name: "ProReview",
    component: ProReview,
  },
  {
    path: "/reports",
    name: "AdminReports",
    component: AdminReports,
    meta: { requiresAuth: true, adminOnly: true },
  },
  {
    path: "/profile/user/:id",
    name: "UserProfile",
    component: AdminProfile,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile/customer/:id",
    name: "CustProfile",
    component: CustProfile,
    
  },
  {
    path: "/profile/professional/:id",   
    name: "ProProfile",
    component: ProProfile,
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
