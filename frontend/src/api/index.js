import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export const getBooks = () => api.get('/books')
export const createBook = (data) => api.post('/books', data)
export const deleteBook = (id) => api.delete(`/books/${id}`)
export const getBookGroups = (bookId) => {
  const params = bookId ? { book_id: bookId } : {}
  return api.get('/books/groups', { params })
}

export const createExcerpt = (data) => api.post('/excerpts', data)
export const getExcerpts = (params) => api.get('/excerpts', { params })
export const getExcerpt = (id) => api.get(`/excerpts/${id}`)
export const updateExcerpt = (id, data) => api.put(`/excerpts/${id}`, data)
export const deleteExcerpt = (id) => api.delete(`/excerpts/${id}`)
export const uploadImage = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/excerpts/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getTags = () => api.get('/tags')
export const createTag = (data) => api.post('/tags', data)
export const deleteTag = (id) => api.delete(`/tags/${id}`)

export default api
