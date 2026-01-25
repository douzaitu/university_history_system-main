// Router configuration - avoiding problematic file references
import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../HomePage.vue";
import People from "../pages/People.vue";
import Places from "../pages/Places.vue";
import Subjects from "../pages/Subjects.vue";
import Organizations from "../pages/Organizations.vue";
import Events from "../pages/Events.vue";
import PersonDetail from "../pages/PersonDetail.vue";
import PlaceDetail from "../pages/PlaceDetail.vue";
import SubjectDetail from "../pages/SubjectDetail.vue";
import OrganizationDetail from "../pages/OrganizationDetail.vue";
import EventDetail from "../pages/EventDetail.vue";
import KnowledgeGraph from "../pages/KnowledgeGraph.vue";

const routes = [
  { path: "/", component: HomePage, meta: { title: "首页" } },
  { path: "/people", component: People, meta: { title: "人物" } },
  { path: "/people/:id", component: PersonDetail, meta: { title: "人物详情" } },
  { path: "/places", component: Places, meta: { title: "地点" } },
  { path: "/places/:id", component: PlaceDetail, meta: { title: "地点详情" } },
  { path: "/subjects", component: Subjects, meta: { title: "学科" } },
  {
    path: "/subjects/:id",
    component: SubjectDetail,
    meta: { title: "学科详情" },
  },
  { path: "/organizations", component: Organizations, meta: { title: "机构" } },
  {
    path: "/organizations/:id",
    component: OrganizationDetail,
    meta: { title: "机构详情" },
  },
  { path: "/events", component: Events, meta: { title: "事件" } },
  { path: "/events/:id", component: EventDetail, meta: { title: "事件详情" } },
  {
    path: "/knowledge-graph",
    name: "KnowledgeGraph",
    component: KnowledgeGraph,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.afterEach((to) => {
  const base = "数字记忆";
  document.title = `${base} · ${to.meta?.title || "CQU"}`;
});

export default router;
