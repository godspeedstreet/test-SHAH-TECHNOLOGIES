import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { Company, CompaniesResponse, SearchParams } from '@/lib/types';

const PAGE_SIZE = 50;

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    
    const search = searchParams.get('search') || '';
    const city = searchParams.get('city') || '';
    const page = parseInt(searchParams.get('page') || '1', 10);
    const pageSize = parseInt(searchParams.get('pageSize') || String(PAGE_SIZE), 10);
    
    const offset = (page - 1) * pageSize;
    
    let whereClause = 'WHERE 1=1';
    const params: unknown[] = [];
    let paramIndex = 1;
    
    if (search) {
      whereClause += ` AND name ILIKE $${paramIndex}`;
      params.push(`%${search}%`);
      paramIndex++;
    }
    
    if (city) {
      whereClause += ` AND city = $${paramIndex}`;
      params.push(city);
      paramIndex++;
    }
    
    const countQuery = `SELECT COUNT(*) as total FROM companies ${whereClause}`;
    const countResult = await query<{ total: string }>(countQuery, params);
    const total = parseInt(countResult[0]?.total || '0', 10);
    
    const dataQuery = `
      SELECT * FROM companies 
      ${whereClause}
      ORDER BY name ASC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;
    params.push(pageSize, offset);
    
    const companies = await query<Company>(dataQuery, params);
    
    const response: CompaniesResponse = {
      companies,
      total,
      page,
      pageSize,
      totalPages: Math.ceil(total / pageSize),
    };
    
    return NextResponse.json(response);
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch companies' },
      { status: 500 }
    );
  }
}