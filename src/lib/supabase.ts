import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || ''
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || ''

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
          reader_id: string
          review: string
          presentation?: string
          rating: number
          read_date: string
          tags: string[]
          genre?: string
          purchase_link?: string
          one_liner?: string
          motivation?: string
          memorable_quotes?: string[]
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          author: string
          reader_id: string
          review: string
          presentation?: string
          rating: number
          read_date: string
          tags: string[]
          genre?: string
          purchase_link?: string
          one_liner?: string
          motivation?: string
          memorable_quotes?: string[]
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          author?: string
          reader_id?: string
          review?: string
          presentation?: string
          rating?: number
          read_date?: string
          tags?: string[]
          genre?: string
          purchase_link?: string
          one_liner?: string
          motivation?: string
          memorable_quotes?: string[]
          created_at?: string
          updated_at?: string
        }
      }
      readers: {
        Row: {
          id: string
          name: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
} 