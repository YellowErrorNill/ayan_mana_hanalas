import { reactive } from 'vue'

export const auth = reactive({
  token: localStorage.getItem('token') || '',
  username: localStorage.getItem('username') || '',
})

export function setAuth(token, username) {
  auth.token = token
  auth.username = username
  localStorage.setItem('token', token)
  localStorage.setItem('username', username)
}

export function clearAuth() {
  auth.token = ''
  auth.username = ''
  localStorage.removeItem('token')
  localStorage.removeItem('username')
}
