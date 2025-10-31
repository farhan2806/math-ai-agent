import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict
import os

class KnowledgeBaseManager:
    def __init__(self, data_path: str = "backend/knowledge_base/math_dataset.json"):
        # NEW ChromaDB API - use PersistentClient
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.client.get_or_create_collection(
            name="math_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.data_path = data_path
        
    def load_and_index(self):
        """Load math dataset and create embeddings"""
        # Check if already indexed
        if self.collection.count() > 0:
            print(f"✅ Knowledge base already loaded with {self.collection.count()} problems")
            return
        
        # Check if file exists
        if not os.path.exists(self.data_path):
            print(f"⚠️ Dataset file not found at {self.data_path}")
            print("Creating sample dataset...")
            self._create_sample_dataset()
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("⚠️ No data found in dataset")
            return
        
        questions = [item['question'] for item in data]
        
        # Create embeddings
        print("Creating embeddings...")
        embeddings = self.model.encode(questions).tolist()
        
        # Prepare metadata - ChromaDB doesn't support lists in metadata
        # Convert steps list to a single string
        metadatas = []
        for item in data:
            metadata = {
                'question': item['question'],
                'solution': item['solution'],
                'steps': ' | '.join(item['steps']),  # Convert list to string with separator
                'topic': item['topic'],
                'difficulty': item['difficulty']
            }
            metadatas.append(metadata)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=questions,
            metadatas=metadatas,
            ids=[f"math_{i}" for i in range(len(data))]
        )
        
        print(f"✅ Indexed {len(data)} math problems")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search for similar questions"""
        try:
            query_embedding = self.model.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            if not results['metadatas'][0]:
                return []
            
            # Convert steps string back to list
            formatted_results = []
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                steps_str = metadata.get('steps', '')
                steps_list = steps_str.split(' | ') if steps_str else []
                
                formatted_results.append({
                    'question': results['documents'][0][i],
                    'solution': metadata.get('solution', ''),
                    'steps': steps_list,
                    'topic': metadata.get('topic', ''),
                    'difficulty': metadata.get('difficulty', ''),
                    'score': 1 - results['distances'][0][i]  # Convert to similarity
                })
            
            return formatted_results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _create_sample_dataset(self):
        """Create sample dataset if file doesn't exist"""
        sample_data = [
            {
                "question": "What is the derivative of x^2?",
                "solution": "The derivative of x^2 is 2x",
                "steps": [
                    "Apply the power rule: d/dx[x^n] = nx^(n-1)",
                    "Here n=2, so derivative = 2x^(2-1) = 2x"
                ],
                "topic": "calculus",
                "difficulty": "easy"
            },
            {
                "question": "Solve the quadratic equation x^2 - 5x + 6 = 0",
                "solution": "x = 2 or x = 3",
                "steps": [
                    "Factor the equation: (x-2)(x-3) = 0",
                    "Set each factor to zero: x-2=0 or x-3=0",
                    "Solve: x=2 or x=3"
                ],
                "topic": "algebra",
                "difficulty": "medium"
            },
            {
                "question": "What is the integral of 2x?",
                "solution": "The integral of 2x is x^2 + C",
                "steps": [
                    "Apply the power rule for integration: ∫x^n dx = x^(n+1)/(n+1) + C",
                    "Here we have 2x = 2x^1",
                    "∫2x dx = 2 * x^(1+1)/(1+1) + C = 2 * x^2/2 + C = x^2 + C"
                ],
                "topic": "calculus",
                "difficulty": "easy"
            },
            {
                "question": "Find the area of a circle with radius 5",
                "solution": "The area is 25π or approximately 78.54 square units",
                "steps": [
                    "Use the formula: Area = πr^2",
                    "Substitute r=5: Area = π(5)^2",
                    "Calculate: Area = 25π ≈ 78.54"
                ],
                "topic": "geometry",
                "difficulty": "easy"
            },
            {
                "question": "What is the Pythagorean theorem?",
                "solution": "In a right triangle, a^2 + b^2 = c^2",
                "steps": [
                    "The Pythagorean theorem states that in a right-angled triangle:",
                    "The square of the hypotenuse (c) equals the sum of squares of the other two sides",
                    "Formula: a^2 + b^2 = c^2, where c is the hypotenuse"
                ],
                "topic": "geometry",
                "difficulty": "easy"
            },
            {
                "question": "Simplify: 3x + 5x - 2x",
                "solution": "6x",
                "steps": [
                    "Combine like terms (all terms with x)",
                    "3x + 5x - 2x = (3 + 5 - 2)x",
                    "= 6x"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            },
            {
                "question": "What is sin(90 degrees)?",
                "solution": "sin(90°) = 1",
                "steps": [
                    "90 degrees is a right angle",
                    "On the unit circle, at 90°, the y-coordinate is 1",
                    "Since sin(θ) = y-coordinate on unit circle, sin(90°) = 1"
                ],
                "topic": "trigonometry",
                "difficulty": "easy"
            },
            {
                "question": "Factor: x^2 + 7x + 12",
                "solution": "(x + 3)(x + 4)",
                "steps": [
                    "Find two numbers that multiply to 12 and add to 7",
                    "Those numbers are 3 and 4 (3 × 4 = 12, 3 + 4 = 7)",
                    "Therefore: x^2 + 7x + 12 = (x + 3)(x + 4)"
                ],
                "topic": "algebra",
                "difficulty": "medium"
            },
            {
                "question": "What is the slope of the line y = 3x + 2?",
                "solution": "The slope is 3",
                "steps": [
                    "The equation is in slope-intercept form: y = mx + b",
                    "Where m is the slope and b is the y-intercept",
                    "In y = 3x + 2, m = 3, so the slope is 3"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            },
            {
                "question": "Calculate: 5! (5 factorial)",
                "solution": "120",
                "steps": [
                    "Factorial means multiply all positive integers up to that number",
                    "5! = 5 × 4 × 3 × 2 × 1",
                    "= 120"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            },
            {
                "question": "What is the volume of a cube with side length 3?",
                "solution": "27 cubic units",
                "steps": [
                    "Volume of cube = side^3",
                    "V = 3^3",
                    "V = 27 cubic units"
                ],
                "topic": "geometry",
                "difficulty": "easy"
            },
            {
                "question": "Solve for x: 2x + 5 = 15",
                "solution": "x = 5",
                "steps": [
                    "Subtract 5 from both sides: 2x = 10",
                    "Divide both sides by 2: x = 5",
                    "Check: 2(5) + 5 = 15 ✓"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            },
            {
                "question": "What is the perimeter of a rectangle with length 8 and width 3?",
                "solution": "22 units",
                "steps": [
                    "Perimeter of rectangle = 2(length + width)",
                    "P = 2(8 + 3)",
                    "P = 2(11) = 22 units"
                ],
                "topic": "geometry",
                "difficulty": "easy"
            },
            {
                "question": "What is cos(0 degrees)?",
                "solution": "cos(0°) = 1",
                "steps": [
                    "At 0 degrees on the unit circle, the point is (1, 0)",
                    "cos(θ) = x-coordinate on unit circle",
                    "Therefore, cos(0°) = 1"
                ],
                "topic": "trigonometry",
                "difficulty": "easy"
            },
            {
                "question": "Expand: (x + 2)^2",
                "solution": "x^2 + 4x + 4",
                "steps": [
                    "Use the formula: (a + b)^2 = a^2 + 2ab + b^2",
                    "Here a = x, b = 2",
                    "(x + 2)^2 = x^2 + 2(x)(2) + 2^2 = x^2 + 4x + 4"
                ],
                "topic": "algebra",
                "difficulty": "medium"
            },
            {
                "question": "Convert 180 degrees to radians",
                "solution": "π radians",
                "steps": [
                    "Use the formula: radians = degrees × (π/180)",
                    "180° × (π/180) = π",
                    "Therefore, 180° = π radians"
                ],
                "topic": "trigonometry",
                "difficulty": "easy"
            },
            {
                "question": "What is the distance between points (0,0) and (3,4)?",
                "solution": "5 units",
                "steps": [
                    "Use the distance formula: d = √[(x2-x1)² + (y2-y1)²]",
                    "d = √[(3-0)² + (4-0)²] = √[9 + 16]",
                    "d = √25 = 5 units"
                ],
                "topic": "geometry",
                "difficulty": "medium"
            },
            {
                "question": "Solve: 3(x - 2) = 12",
                "solution": "x = 6",
                "steps": [
                    "Distribute the 3: 3x - 6 = 12",
                    "Add 6 to both sides: 3x = 18",
                    "Divide by 3: x = 6"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            },
            {
                "question": "What is the sum of angles in a triangle?",
                "solution": "180 degrees",
                "steps": [
                    "This is a fundamental theorem in Euclidean geometry",
                    "In any triangle, the three interior angles always sum to 180°",
                    "This applies to all types of triangles: acute, right, and obtuse"
                ],
                "topic": "geometry",
                "difficulty": "easy"
            },
            {
                "question": "Simplify: √(16)",
                "solution": "4",
                "steps": [
                    "Find the number that when multiplied by itself equals 16",
                    "4 × 4 = 16",
                    "Therefore, √16 = 4"
                ],
                "topic": "algebra",
                "difficulty": "easy"
            }
        ]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # Write sample data
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2)
        
        print(f"✅ Created sample dataset at {self.data_path}")