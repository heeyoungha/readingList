import { supabase } from './supabase'
import { Book } from '../types/book'
import { ActionList } from '../types/actionList'

// Get all books with reader names
export async function getBooks(): Promise<Book[]> {
  const { data, error } = await supabase
    .from('books')
    .select(`
      *,
      readers!inner(name)
    `)
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching books:', error)
    throw error
  }

  console.log('Raw book data from database:', data); // 디버깅용

  return data?.map(book => ({
    id: book.id,
    title: book.title,
    author: book.author,
    reader_id: book.reader_id,
    reader_name: book.readers.name,
    review: book.review,
    presentation: book.presentation,
    rating: book.rating,
    readDate: book.read_date,
    tags: book.tags,
    genre: book.genre,
    purchaseLink: book.purchase_link,
    oneLiner: book.one_liner,
    motivation: book.motivation,
    memorableQuotes: book.memorable_quotes
  })) || []
}

// Add a new book
export async function addBook(book: Omit<Book, 'id' | 'reader_name'>): Promise<Book> {
  console.log('addBook called with:', book);
  
  const insertData = {
    title: book.title,
    author: book.author,
    reader_id: book.reader_id,
    review: book.review,
    presentation: book.presentation,
    rating: book.rating,
    read_date: book.readDate,
    tags: book.tags,
    genre: book.genre,
    purchase_link: book.purchaseLink,
    one_liner: book.oneLiner,
    motivation: book.motivation,
    memorable_quotes: book.memorableQuotes
  };
  
  console.log('Inserting data:', insertData);
  
  const { data, error } = await supabase
    .from('books')
    .insert(insertData)
    .select(`
      *,
      readers!inner(name)
    `)
    .single()

  if (error) {
    console.error('Error adding book:', error)
    throw error
  }

  console.log('Book added to database:', data);

  return {
    id: data.id,
    title: data.title,
    author: data.author,
    reader_id: data.reader_id,
    reader_name: data.readers.name,
    review: data.review,
    presentation: data.presentation,
    rating: data.rating,
    readDate: data.read_date,
    tags: data.tags,
    genre: data.genre,
    purchaseLink: data.purchase_link,
    oneLiner: data.one_liner,
    motivation: data.motivation,
    memorableQuotes: data.memorable_quotes
  }
}

// Update a book
export async function updateBook(id: string, updates: Partial<Book>): Promise<Book> {
  const updateData: any = {}
  
  if (updates.title) updateData.title = updates.title
  if (updates.author) updateData.author = updates.author
  if (updates.reader_id) updateData.reader_id = updates.reader_id
  if (updates.review) updateData.review = updates.review
  if (updates.presentation !== undefined) updateData.presentation = updates.presentation
  if (updates.rating) updateData.rating = updates.rating
  if (updates.readDate) updateData.read_date = updates.readDate
  if (updates.tags) updateData.tags = updates.tags
  if (updates.genre) updateData.genre = updates.genre
  if (updates.purchaseLink) updateData.purchase_link = updates.purchaseLink
  if (updates.oneLiner) updateData.one_liner = updates.oneLiner
  if (updates.motivation) updateData.motivation = updates.motivation
  if (updates.memorableQuotes) updateData.memorable_quotes = updates.memorableQuotes

  const { data, error } = await supabase
    .from('books')
    .update(updateData)
    .eq('id', id)
    .select(`
      *,
      readers!inner(name)
    `)
    .single()

  if (error) {
    console.error('Error updating book:', error)
    throw error
  }

  return {
    id: data.id,
    title: data.title,
    author: data.author,
    reader_id: data.reader_id,
    reader_name: data.readers.name,
    review: data.review,
    presentation: data.presentation,
    rating: data.rating,
    readDate: data.read_date,
    tags: data.tags,
    genre: data.genre,
    purchaseLink: data.purchase_link,
    oneLiner: data.one_liner,
    motivation: data.motivation,
    memorableQuotes: data.memorable_quotes
  }
}

// Delete a book
export async function deleteBook(id: string): Promise<void> {
  const { error } = await supabase
    .from('books')
    .delete()
    .eq('id', id)

  if (error) {
    console.error('Error deleting book:', error)
    throw error
  }
}

// Get all readers
export async function getReaders(): Promise<{ id: string; name: string; email?: string; bio?: string }[]> {
  const { data, error } = await supabase
    .from('readers')
    .select('id, name, email, bio')
    .order('name')

  if (error) {
    console.error('Error fetching readers:', error)
    throw error
  }

  return data || []
}

// Add a new reader
export async function addReader(name: string, email?: string, bio?: string): Promise<{ id: string; name: string; email?: string; bio?: string }> {
  const { data, error } = await supabase
    .from('readers')
    .insert({ name, email, bio })
    .select()
    .single()

  if (error) {
    console.error('Error adding reader:', error)
    throw error
  }

  return data
}

// Delete a reader
export async function deleteReader(id: string): Promise<void> {
  const { error } = await supabase
    .from('readers')
    .delete()
    .eq('id', id)

  if (error) {
    console.error('Error deleting reader:', error)
    throw error
  }
}

// Add sample data
export async function addSampleData(): Promise<void> {
  try {
    // First, add sample readers
    const readers = [
      { name: '김독서', email: 'kim@example.com', bio: '과학과 철학에 관심이 많은 독서가' },
      { name: '이북러버', email: 'lee@example.com', bio: '소설과 문학 작품을 즐겨 읽는 독자' },
      { name: '박철학', email: 'park@example.com', bio: '철학과 자기계발 서적을 선호하는 독자' },
      { name: '정역사', email: 'jung@example.com', bio: '역사와 인문학 서적을 주로 읽는 독자' }
    ];

    for (const reader of readers) {
      try {
        await addReader(reader.name, reader.email, reader.bio);
      } catch (error) {
        // Reader might already exist, continue
        console.log(`Reader ${reader.name} might already exist`);
      }
    }

    // Get reader IDs for sample books
    const allReaders = await getReaders();
    const readerMap = new Map(allReaders.map(r => [r.name, r.id]));

    // Add sample books
    const sampleBooks = [
      {
        title: '코스모스',
        author: '칼 세이건',
        reader_id: readerMap.get('김독서') || allReaders[0]?.id,
        review: '우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다. 세이건의 시적인 문체로 복잡한 과학 개념들을 쉽게 설명해주어 과학에 대한 흥미를 불러일으켰습니다.',
        presentation: '우주에 대한 경이로움과 과학적 사고의 중요성을 깨닫게 해준 책입니다. 세이건의 시적인 문체로 복잡한 과학 개념들을 쉽게 설명해주어 과학에 대한 흥미를 불러일으켰습니다.',
        rating: 5,
        emotion: 'excited' as const,
        readDate: '2024-01-15',
        tags: ['과학', '우주', '철학']
      },
      {
        title: '82년생 김지영',
        author: '조남주',
        reader_id: readerMap.get('이북러버') || allReaders[0]?.id,
        review: '현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다. 읽으면서 많은 생각을 하게 되었고, 우리 사회에 대해 돌아보는 계기가 되었습니다.',
        presentation: '현대 여성이 겪는 현실적인 문제들을 담담하게 그려낸 작품입니다. 읽으면서 많은 생각을 하게 되었고, 우리 사회에 대해 돌아보는 계기가 되었습니다.',
        rating: 4,
        emotion: 'thoughtful' as const,
        readDate: '2024-01-28',
        tags: ['소설', '여성', '사회']
      },
      {
        title: '미움받을 용기',
        author: '기시미 이치로, 고가 후미타케',
        reader_id: readerMap.get('박철학') || allReaders[0]?.id,
        review: '아들러 심리학을 바탕으로 한 대화형식의 책입니다. 타인의 시선에서 벗어나 자신만의 삶을 살아가는 것의 중요성을 배웠습니다. 실천하기는 어렵지만 좋은 방향을 제시해주는 책이었습니다.',
        presentation: '아들러 심리학을 바탕으로 한 대화형식의 책입니다. 타인의 시선에서 벗어나 자신만의 삶을 살아가는 것의 중요성을 배웠습니다. 실천하기는 어렵지만 좋은 방향을 제시해주는 책이었습니다.',
        rating: 4,
        emotion: 'calm' as const,
        readDate: '2024-02-10',
        tags: ['자기계발', '심리학', '철학']
      }
    ];

    for (const book of sampleBooks) {
      try {
        await addBook(book);
      } catch (error) {
        console.log(`Book ${book.title} might already exist`);
      }
    }

    console.log('Sample data added successfully');
  } catch (error) {
    console.error('Error adding sample data:', error);
    throw error;
  }
} 

// Get all action lists with reader names
export async function getActionLists(): Promise<ActionList[]> {
  const { data, error } = await supabase
    .from('action_lists')
    .select(`
      *,
      readers!inner(name)
    `)
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching action lists:', error)
    throw error
  }

  return data?.map(actionList => ({
    id: actionList.id,
    title: actionList.title,
    reader_id: actionList.reader_id,
    reader_name: actionList.readers.name,
    book_title: actionList.book_title,
    content: actionList.content,
    target_months: actionList.target_months,
    action_time: actionList.action_time,
    status: actionList.status,
    created_at: actionList.created_at,
    updated_at: actionList.updated_at
  })) || []
}

// Add a new action list
export async function addActionList(actionList: Omit<ActionList, 'id' | 'reader_name' | 'created_at' | 'updated_at'>): Promise<ActionList> {
  const insertData = {
    title: actionList.title,
    reader_id: actionList.reader_id,
    book_title: actionList.book_title,
    content: actionList.content,
    target_months: actionList.target_months,
    action_time: actionList.action_time,
    status: actionList.status
  };

  const { data, error } = await supabase
    .from('action_lists')
    .insert(insertData)
    .select(`
      *,
      readers!inner(name)
    `)
    .single()

  if (error) {
    console.error('Error adding action list:', error)
    throw error
  }

  return {
    id: data.id,
    title: data.title,
    reader_id: data.reader_id,
    reader_name: data.readers.name,
    book_title: data.book_title,
    content: data.content,
    target_months: data.target_months,
    status: data.status,
    created_at: data.created_at,
    updated_at: data.updated_at
  }
}

// Update an action list
export async function updateActionList(id: string, updates: Partial<ActionList>): Promise<ActionList> {
  const updateData: any = {}
  
  if (updates.title) updateData.title = updates.title
  if (updates.reader_id) updateData.reader_id = updates.reader_id
  if (updates.book_title) updateData.book_title = updates.book_title
  if (updates.content) updateData.content = updates.content
  if (updates.target_months) updateData.target_months = updates.target_months
  if (updates.action_time) updateData.action_time = updates.action_time
  if (updates.status) updateData.status = updates.status

  const { data, error } = await supabase
    .from('action_lists')
    .update(updateData)
    .eq('id', id)
    .select(`
      *,
      readers!inner(name)
    `)
    .single()

  if (error) {
    console.error('Error updating action list:', error)
    throw error
  }

  return {
    id: data.id,
    title: data.title,
    reader_id: data.reader_id,
    reader_name: data.readers.name,
    book_title: data.book_title,
    content: data.content,
    target_months: data.target_months,
    action_time: data.action_time,
    status: data.status,
    created_at: data.created_at,
    updated_at: data.updated_at
  }
}

// Delete an action list
export async function deleteActionList(id: string): Promise<void> {
  const { error } = await supabase
    .from('action_lists')
    .delete()
    .eq('id', id)

  if (error) {
    console.error('Error deleting action list:', error)
    throw error
  }
} 