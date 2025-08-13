'use client';

import { API_BASE_URL } from '@/app/components/config';
import { DeleteResponse } from '../types';

// --- API Functions ---

export async function deleteDataset(datasetId: string, token: string): Promise<DeleteResponse> {
  try {
    const url = `${API_BASE_URL}/api/v1/datasets/${datasetId}`;
    
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });


    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: DeleteResponse = await res.json();
    return data;

  } catch (error) {
    console.error("Error deleting dataset:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
}

export async function deleteExperiment(experimentId: string, datasetId: string, token: string): Promise<DeleteResponse> {
  try {
    const url = `${API_BASE_URL}/api/v1/experiments/${experimentId}?dataset_id=${datasetId}`;
    
    const res = await fetch(url, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });


    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: DeleteResponse = await res.json();
    return data;

  } catch (error) {
    console.error("Error deleting experiment:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
}
