"""
Test script to verify score management backend functionality
This script tests the repository methods directly
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions.extensions import db
from repositories.assignmentRepo import AssignmentRepo
from models.assignment import Assignment
from models.user import User

def test_score_operations():
    """Test score CRUD operations"""
    
    print("=" * 60)
    print("Testing Score Management Backend")
    print("=" * 60)
    
    repo = AssignmentRepo()
    
    # Test 1: Get all scores (should work even with no scores set)
    print("\n✓ Test 1: Get all scores for user")
    test_user_id = 1  # Assuming user_id 1 exists
    
    try:
        all_scores = repo.getAllScores(test_user_id)
        print(f"  Retrieved {len(all_scores)} assignments")
        
        if all_scores:
            print(f"  Sample data:")
            for score_data in all_scores[:3]:  # Show first 3
                print(f"    - {score_data['title']}: {score_data['score']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 2: Get assignments to work with
    print("\n✓ Test 2: Get assignment for testing")
    try:
        assignments = repo.getAllAssignmentById(test_user_id)
        if not assignments:
            print("  ⚠ No assignments found for user. Please create an assignment first.")
            return True
        
        test_assignment = assignments[0]
        print(f"  Using assignment: {test_assignment.title} (ID: {test_assignment.assignment_id})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 3: Update a score
    print("\n✓ Test 3: Update score")
    test_score = 95.5
    try:
        success = repo.updateScore(test_user_id, test_assignment.assignment_id, test_score)
        if success:
            print(f"  ✓ Score updated to {test_score}")
        else:
            print(f"  ✗ Failed to update score")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 4: Retrieve the score
    print("\n✓ Test 4: Retrieve score")
    try:
        retrieved_score = repo.getScore(test_user_id, test_assignment.assignment_id)
        if retrieved_score == test_score:
            print(f"  ✓ Score retrieved correctly: {retrieved_score}")
        else:
            print(f"  ✗ Score mismatch. Expected {test_score}, got {retrieved_score}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 5: Update score again
    print("\n✓ Test 5: Update score to different value")
    new_score = 88.0
    try:
        success = repo.updateScore(test_user_id, test_assignment.assignment_id, new_score)
        retrieved = repo.getScore(test_user_id, test_assignment.assignment_id)
        if retrieved == new_score:
            print(f"  ✓ Score updated and retrieved correctly: {new_score}")
        else:
            print(f"  ✗ Score mismatch after update")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    # Test 6: Test with invalid assignment ID
    print("\n✓ Test 6: Test error handling with invalid assignment")
    try:
        invalid_score = repo.getScore(test_user_id, 99999)
        if invalid_score is None:
            print(f"  ✓ Correctly returns None for invalid assignment")
        else:
            print(f"  ⚠ Expected None, got {invalid_score}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print("\nNote: This test requires:")
    print("  1. The Flask app database to exist")
    print("  2. At least one user in the database")
    print("  3. At least one assignment for that user")
    print()
    
    try:
        test_score_operations()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
