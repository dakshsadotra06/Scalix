#!/usr/bin/env python3
"""
StartupOps Backend API Testing Suite
Tests all endpoints including auth, startups, tasks, team, feedback, analytics, AI, and payments
"""

import requests
import sys
import json
from datetime import datetime
import time

class StartupOpsAPITester:
    def __init__(self, base_url="https://startup-toolkit-8.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None
        self.user_id = None
        self.startup_id = None
        self.task_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "PASS")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                self.log(f"Response: {response.text[:200]}", "ERROR")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}", "ERROR")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_auth_signup(self):
        """Test user signup"""
        timestamp = int(time.time())
        test_data = {
            "email": f"test.user.{timestamp}@example.com",
            "password": "TestPass123!",
            "name": f"Test User {timestamp}"
        }
        
        success, response = self.run_test(
            "Auth Signup",
            "POST",
            "auth/signup",
            200,
            data=test_data
        )
        
        if success and 'token' in response:
            self.session_token = response['token']
            self.user_id = response['user_id']
            self.log(f"Session token obtained: {self.session_token[:20]}...")
            return True
        return False

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test(
            "Auth Me",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_startup(self):
        """Test startup creation"""
        startup_data = {
            "name": f"Test Startup {int(time.time())}",
            "description": "A test startup for API testing",
            "industry": "Technology",
            "vision": "To revolutionize testing"
        }
        
        success, response = self.run_test(
            "Create Startup",
            "POST",
            "startups",
            200,
            data=startup_data
        )
        
        if success and 'startup_id' in response:
            self.startup_id = response['startup_id']
            self.log(f"Startup created: {self.startup_id}")
            return True
        return False

    def test_get_startups(self):
        """Test get user startups"""
        success, response = self.run_test(
            "Get Startups",
            "GET",
            "startups",
            200
        )
        return success

    def test_get_startup_details(self):
        """Test get specific startup"""
        if not self.startup_id:
            return False
            
        success, response = self.run_test(
            "Get Startup Details",
            "GET",
            f"startups/{self.startup_id}",
            200
        )
        return success

    def test_update_startup(self):
        """Test startup update"""
        if not self.startup_id:
            return False
            
        update_data = {
            "description": "Updated description for testing",
            "vision": "Updated vision statement"
        }
        
        success, response = self.run_test(
            "Update Startup",
            "PUT",
            f"startups/{self.startup_id}",
            200,
            data=update_data
        )
        return success

    def test_create_task(self):
        """Test task creation"""
        if not self.startup_id:
            return False
            
        task_data = {
            "title": "Test Task",
            "description": "A test task for API testing",
            "priority": "high",
            "status": "todo"
        }
        
        success, response = self.run_test(
            "Create Task",
            "POST",
            f"startups/{self.startup_id}/tasks",
            200,
            data=task_data
        )
        
        if success and 'task_id' in response:
            self.task_id = response['task_id']
            return True
        return False

    def test_get_tasks(self):
        """Test get startup tasks"""
        if not self.startup_id:
            return False
            
        success, response = self.run_test(
            "Get Tasks",
            "GET",
            f"startups/{self.startup_id}/tasks",
            200
        )
        return success

    def test_update_task(self):
        """Test task update"""
        if not self.startup_id or not self.task_id:
            return False
            
        update_data = {
            "status": "in_progress",
            "description": "Updated task description"
        }
        
        success, response = self.run_test(
            "Update Task",
            "PUT",
            f"startups/{self.startup_id}/tasks/{self.task_id}",
            200,
            data=update_data
        )
        return success

    def test_team_management(self):
        """Test team endpoints"""
        if not self.startup_id:
            return False
            
        # Get team
        success1, _ = self.run_test(
            "Get Team",
            "GET",
            f"startups/{self.startup_id}/team",
            200
        )
        
        # Try to invite team member (will be pending since user doesn't exist)
        invite_data = {
            "email": "nonexistent@example.com",
            "role": "member"
        }
        
        success2, _ = self.run_test(
            "Invite Team Member",
            "POST",
            f"startups/{self.startup_id}/team/invite",
            200,
            data=invite_data
        )
        
        return success1 and success2

    def test_feedback_system(self):
        """Test feedback endpoints"""
        if not self.startup_id:
            return False
            
        # Create feedback
        feedback_data = {
            "content": "Great progress on the MVP!",
            "rating": 5,
            "tags": ["positive", "mvp"],
            "source": "internal"
        }
        
        success1, _ = self.run_test(
            "Create Feedback",
            "POST",
            f"startups/{self.startup_id}/feedback",
            200,
            data=feedback_data
        )
        
        # Get feedback
        success2, _ = self.run_test(
            "Get Feedback",
            "GET",
            f"startups/{self.startup_id}/feedback",
            200
        )
        
        return success1 and success2

    def test_analytics(self):
        """Test analytics endpoint"""
        if not self.startup_id:
            return False
            
        success, response = self.run_test(
            "Get Analytics",
            "GET",
            f"startups/{self.startup_id}/analytics",
            200
        )
        
        if success:
            self.log(f"Analytics data keys: {list(response.keys())}")
        
        return success

    def test_ai_chat(self):
        """Test AI chat functionality"""
        if not self.startup_id:
            return False
            
        chat_data = {
            "message": "What are some good strategies for user acquisition?"
        }
        
        success, response = self.run_test(
            "AI Chat",
            "POST",
            f"startups/{self.startup_id}/ai/chat",
            200,
            data=chat_data
        )
        
        if success and 'response' in response:
            self.log(f"AI Response received: {len(response['response'])} characters")
        
        return success

    def test_ai_pitch_generation(self):
        """Test AI pitch generation"""
        if not self.startup_id:
            return False
            
        success, response = self.run_test(
            "AI Pitch Generation",
            "POST",
            f"startups/{self.startup_id}/ai/pitch",
            200,
            data={}
        )
        
        if success and 'pitch_outline' in response:
            self.log(f"Pitch outline generated: {len(response['pitch_outline'])} characters")
        
        return success

    def test_payment_checkout(self):
        """Test payment checkout session creation"""
        checkout_data = {
            "origin_url": self.base_url,
            "package": "pro"
        }
        
        success, response = self.run_test(
            "Create Checkout Session",
            "POST",
            "payments/checkout/session",
            200,
            data=checkout_data
        )
        
        if success and 'url' in response:
            self.log(f"Checkout URL created: {response['url'][:50]}...")
        
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("Starting StartupOps API Test Suite")
        self.log(f"Testing against: {self.base_url}")
        
        # Authentication Tests
        self.log("\n=== AUTHENTICATION TESTS ===")
        if not self.test_auth_signup():
            self.log("❌ Auth signup failed - stopping tests", "ERROR")
            return False
            
        self.test_auth_me()
        
        # Startup Management Tests
        self.log("\n=== STARTUP MANAGEMENT TESTS ===")
        if not self.test_create_startup():
            self.log("❌ Startup creation failed - skipping dependent tests", "ERROR")
        else:
            self.test_get_startups()
            self.test_get_startup_details()
            self.test_update_startup()
        
        # Task Management Tests
        self.log("\n=== TASK MANAGEMENT TESTS ===")
        if self.startup_id:
            self.test_create_task()
            self.test_get_tasks()
            self.test_update_task()
        
        # Team Management Tests
        self.log("\n=== TEAM MANAGEMENT TESTS ===")
        if self.startup_id:
            self.test_team_management()
        
        # Feedback System Tests
        self.log("\n=== FEEDBACK SYSTEM TESTS ===")
        if self.startup_id:
            self.test_feedback_system()
        
        # Analytics Tests
        self.log("\n=== ANALYTICS TESTS ===")
        if self.startup_id:
            self.test_analytics()
        
        # AI Features Tests
        self.log("\n=== AI FEATURES TESTS ===")
        if self.startup_id:
            self.test_ai_chat()
            self.test_ai_pitch_generation()
        
        # Payment Tests
        self.log("\n=== PAYMENT TESTS ===")
        self.test_payment_checkout()
        
        # Final Results
        self.log(f"\n=== TEST RESULTS ===")
        self.log(f"Tests Run: {self.tests_run}")
        self.log(f"Tests Passed: {self.tests_passed}")
        self.log(f"Tests Failed: {self.tests_run - self.tests_passed}")
        self.log(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log("\n=== FAILED TESTS ===")
            for failure in self.failed_tests:
                self.log(f"❌ {failure}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = StartupOpsAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())