import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const cities = await query<{ city: string }>(
      `SELECT DISTINCT city FROM companies WHERE city IS NOT NULL AND city != '' ORDER BY city ASC`
    );
    
    return NextResponse.json(cities.map(c => c.city));
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cities' },
      { status: 500 }
    );
  }
}