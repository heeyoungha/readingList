import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_UPABASE_URL || ''
const supabaseAnonKey = process.env.REACT_APP_UPABASE_ANON_KEY || ''

// Supabase configuration

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface Database {
  public: {
    Tables: {
      books: {
        Row: {
          id: string
          title: string
          author: string
          reader: string
          review: string
          rating: number
          emotion: string
          read_date: string
          tags: string[]
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          author: string
          reader: string
          review: string
          rating: number
          emotion: string
          read_date: string
          tags: string[]
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          author?: string
          reader?: string
          review?: string
          rating?: number
          emotion?: string
          read_date?: string
          tags?: string[]
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
} 