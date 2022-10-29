import { createRouter, createWebHashHistory } from 'vue-router'
import Dummy from '../views/Dummy.vue'
import HomeView from '../views/HomeView.vue'
import UserDetails from '../views/UserDetails.vue'
import UserSearch from '../views/UserSearch.vue'
import LeaveRule from "../views/LeaveRule.vue"
import LeaveRuleSearch from "../views/LeaveRuleSearch.vue"
import LeaveApplication from "../views/LeaveApplication.vue"
import LeaveApplicationSearch from "../views/LeaveApplicationSearch.vue"
import FacultyActivityCredits from "../views/FacultyActivityCredits.vue"
import FacultyActivity from "../views/FacultyActivity.vue"
import FacultyActivitySearch from "../views/FacultyActivitySearch.vue"
import WorkRequest from "../views/WorkRequest.vue"
import WorkRequestSearch from "../views/WorkRequestSearch.vue"
import LeaveStatus from "../views/LeaveStatus.vue"
import FormAction from "../views/FormAction.vue"
import CalendarHolidays from "../views/CalendarHolidays.vue"

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/dummy',
      name: 'Dummy',
      component: Dummy
    },
    {
      path: '/',
      name: 'HomeView',
      component: HomeView
    },
    {
      path: '/user/:id?',
      name: 'UserDetails',
      component: UserDetails
    },
    {
      path: '/user.find',
      name: 'UserSearch',
      component: UserSearch
    },
    {
      path: '/rule/:id?',
      name: 'LeaveRule',
      component: LeaveRule
    },
    {
      path: '/rule.find',
      name: 'LeaveRuleSearch',
      component: LeaveRuleSearch
    },
    {
      path: '/leave/:id?',
      name: 'LeaveApplication',
      component: LeaveApplication
    },
    {
      path: '/leave.find',
      name: 'LeaveApplicationSearch',
      component: LeaveApplicationSearch
    },
    {
      path: '/fa.credits',
      name: 'FacultyActivityCredits',
      component: FacultyActivityCredits
    },
    {
      path: '/fa/:id?',
      name: 'FacultyActivity',
      component: FacultyActivity
    },
    {
      path: '/wreq/:id?',
      name: 'WorkRequest',
      component: WorkRequest
    },
    {
      path: '/wreq.find',
      name: 'WorkRequestSearch',
      component: WorkRequestSearch
    },
    {
      path: '/leaves.status/:id?',
      name: 'LeaveStatus',
      component: LeaveStatus
    },
    {
      path: '/fa.find',
      name: 'FacultyActivitySearch',
      component: FacultyActivitySearch
    },
    {
      path: '/form.actions',
      name: 'FormAction',
      component: FormAction
    },
    {
      path: '/calhol',
      name: 'CalendarHolidays',
      component: CalendarHolidays
    }
  ]
})

export default router
