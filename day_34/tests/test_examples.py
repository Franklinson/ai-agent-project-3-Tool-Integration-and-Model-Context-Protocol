import json
import unittest
from pathlib import Path
from collections import defaultdict


class TestExampleEffectiveness(unittest.TestCase):
    """Test example completeness, clarity, and coverage"""
    
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = Path("day_34/examples")
        cls.example_files = [
            "email_tool_examples.json",
            "database_query_examples.json",
            "web_search_examples.json"
        ]
        cls.examples_data = {}
        
        for file in cls.example_files:
            with open(cls.examples_dir / file) as f:
                cls.examples_data[file] = json.load(f)
    
    # COMPLETENESS TESTS
    
    def test_all_categories_present(self):
        """Test that all required categories are present"""
        required_categories = ['common_use_cases', 'advanced_use_cases', 'edge_cases', 'error_cases']
        
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                for category in required_categories:
                    self.assertIn(category, data['examples'], 
                                f"{file} missing category: {category}")
    
    def test_minimum_examples_per_category(self):
        """Test minimum number of examples per category"""
        min_requirements = {
            'common_use_cases': 3,
            'advanced_use_cases': 1,
            'edge_cases': 1,
            'error_cases': 1
        }
        
        for file, data in self.examples_data.items():
            for category, min_count in min_requirements.items():
                with self.subTest(file=file, category=category):
                    examples = data['examples'][category]
                    self.assertGreaterEqual(len(examples), min_count,
                                          f"{file} {category} has {len(examples)} examples, need {min_count}")
    
    def test_example_has_all_fields(self):
        """Test that each example has required fields"""
        required_fields = ['name', 'description', 'input', 'output']
        
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        for field in required_fields:
                            self.assertIn(field, example,
                                        f"{file} {category}[{idx}] missing {field}")
    
    def test_input_not_empty(self):
        """Test that input is not empty"""
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        self.assertTrue(example['input'],
                                      f"{file} {category}[{idx}] has empty input")
    
    def test_output_not_empty(self):
        """Test that output is not empty"""
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        self.assertIsNotNone(example['output'],
                                           f"{file} {category}[{idx}] has None output")
    
    # CLARITY TESTS
    
    def test_name_is_descriptive(self):
        """Test that example names are descriptive (not too short)"""
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        name = example['name']
                        self.assertGreater(len(name), 3,
                                         f"{file} {category}[{idx}] name too short: '{name}'")
    
    def test_description_is_meaningful(self):
        """Test that descriptions are meaningful (not too short)"""
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        desc = example['description']
                        self.assertGreater(len(desc), 10,
                                         f"{file} {category}[{idx}] description too short")
    
    def test_error_cases_have_error_field(self):
        """Test that error cases have 'error' field in output"""
        for file, data in self.examples_data.items():
            examples = data['examples']['error_cases']
            for idx, example in enumerate(examples):
                with self.subTest(file=file, index=idx):
                    self.assertIn('error', example['output'],
                                f"{file} error_cases[{idx}] missing 'error' field")
    
    def test_success_cases_no_error_field(self):
        """Test that success cases don't have 'error' field"""
        success_categories = ['common_use_cases', 'advanced_use_cases', 'edge_cases']
        
        for file, data in self.examples_data.items():
            for category in success_categories:
                examples = data['examples'][category]
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        self.assertNotIn('error', example['output'],
                                       f"{file} {category}[{idx}] has 'error' field")
    
    # COVERAGE TESTS
    
    def test_covers_basic_functionality(self):
        """Test that common use cases cover basic functionality"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                common = data['examples']['common_use_cases']
                self.assertGreaterEqual(len(common), 3,
                                      f"{file} needs more common use cases")
    
    def test_covers_complex_scenarios(self):
        """Test that advanced cases exist"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                advanced = data['examples']['advanced_use_cases']
                self.assertGreater(len(advanced), 0,
                                 f"{file} needs advanced use cases")
    
    def test_covers_edge_cases(self):
        """Test that edge cases are covered"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                edge = data['examples']['edge_cases']
                self.assertGreater(len(edge), 0,
                                 f"{file} needs edge cases")
    
    def test_covers_error_scenarios(self):
        """Test that error scenarios are covered"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                errors = data['examples']['error_cases']
                self.assertGreater(len(errors), 0,
                                 f"{file} needs error cases")
    
    def test_parameter_variety(self):
        """Test that examples use different parameter combinations"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                all_examples = []
                for category in ['common_use_cases', 'advanced_use_cases']:
                    all_examples.extend(data['examples'][category])
                
                # Check that we have variety in inputs
                input_keys = [set(ex['input'].keys()) for ex in all_examples]
                unique_combinations = len(set(frozenset(keys) for keys in input_keys))
                
                self.assertGreater(unique_combinations, 1,
                                 f"{file} lacks parameter variety")
    
    def test_realistic_data(self):
        """Test that examples use realistic data"""
        for file, data in self.examples_data.items():
            for category, examples in data['examples'].items():
                for idx, example in enumerate(examples):
                    with self.subTest(file=file, category=category, index=idx):
                        # Check that strings are not just placeholders
                        input_str = json.dumps(example['input'])
                        self.assertNotIn('xxx', input_str.lower(),
                                       f"{file} {category}[{idx}] uses placeholder data")
                        self.assertNotIn('placeholder', input_str.lower(),
                                       f"{file} {category}[{idx}] uses placeholder data")
    
    # QUALITY METRICS
    
    def test_generate_coverage_report(self):
        """Generate coverage report for all tools"""
        report = {}
        
        for file, data in self.examples_data.items():
            tool_name = data['tool_name']
            stats = {
                'common': len(data['examples']['common_use_cases']),
                'advanced': len(data['examples']['advanced_use_cases']),
                'edge': len(data['examples']['edge_cases']),
                'error': len(data['examples']['error_cases']),
                'total': sum(len(examples) for examples in data['examples'].values())
            }
            report[tool_name] = stats
        
        # Print report
        print("\n" + "="*60)
        print("EXAMPLE COVERAGE REPORT")
        print("="*60)
        for tool, stats in report.items():
            print(f"\n{tool}:")
            print(f"  Common use cases: {stats['common']}")
            print(f"  Advanced cases:   {stats['advanced']}")
            print(f"  Edge cases:       {stats['edge']}")
            print(f"  Error cases:      {stats['error']}")
            print(f"  Total examples:   {stats['total']}")
        print("="*60 + "\n")
        
        # Assert minimum total
        for tool, stats in report.items():
            self.assertGreaterEqual(stats['total'], 8,
                                  f"{tool} needs at least 8 total examples")


class TestExampleQuality(unittest.TestCase):
    """Test example quality and usefulness"""
    
    @classmethod
    def setUpClass(cls):
        cls.examples_dir = Path("day_34/examples")
        cls.example_files = [
            "email_tool_examples.json",
            "database_query_examples.json",
            "web_search_examples.json"
        ]
        cls.examples_data = {}
        
        for file in cls.example_files:
            with open(cls.examples_dir / file) as f:
                cls.examples_data[file] = json.load(f)
    
    def test_unique_example_names(self):
        """Test that example names are unique within each file"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                all_names = []
                for examples in data['examples'].values():
                    all_names.extend([ex['name'] for ex in examples])
                
                self.assertEqual(len(all_names), len(set(all_names)),
                               f"{file} has duplicate example names")
    
    def test_progressive_complexity(self):
        """Test that examples progress from simple to complex"""
        for file, data in self.examples_data.items():
            with self.subTest(file=file):
                common = data['examples']['common_use_cases']
                advanced = data['examples']['advanced_use_cases']
                
                # Advanced should have more parameters on average
                common_params = sum(len(ex['input']) for ex in common) / len(common)
                advanced_params = sum(len(ex['input']) for ex in advanced) / len(advanced)
                
                self.assertGreaterEqual(advanced_params, common_params * 0.8,
                                      f"{file} advanced cases not more complex")
    
    def test_error_messages_informative(self):
        """Test that error messages are informative"""
        for file, data in self.examples_data.items():
            errors = data['examples']['error_cases']
            for idx, example in enumerate(errors):
                with self.subTest(file=file, index=idx):
                    output = example['output']
                    self.assertIn('message', output,
                                f"{file} error_cases[{idx}] missing error message")
                    self.assertGreater(len(output['message']), 10,
                                     f"{file} error_cases[{idx}] error message too short")


def generate_improvement_report():
    """Generate report of potential improvements"""
    examples_dir = Path("day_34/examples")
    improvements = defaultdict(list)
    
    for file in ["email_tool_examples.json", "database_query_examples.json", "web_search_examples.json"]:
        with open(examples_dir / file) as f:
            data = json.load(f)
        
        tool_name = data['tool_name']
        
        # Check for improvement opportunities
        total = sum(len(examples) for examples in data['examples'].values())
        if total < 12:
            improvements[tool_name].append(f"Consider adding more examples (current: {total})")
        
        # Check error case coverage
        error_count = len(data['examples']['error_cases'])
        if error_count < 3:
            improvements[tool_name].append(f"Add more error cases (current: {error_count})")
        
        # Check for documentation
        if 'description' not in data:
            improvements[tool_name].append("Add tool-level description")
    
    return improvements


if __name__ == "__main__":
    # Run tests
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate improvement report
    print("\n" + "="*60)
    print("IMPROVEMENT RECOMMENDATIONS")
    print("="*60)
    improvements = generate_improvement_report()
    
    if improvements:
        for tool, items in improvements.items():
            print(f"\n{tool}:")
            for item in items:
                print(f"  • {item}")
    else:
        print("\nNo improvements needed - all examples meet quality standards!")
    
    print("="*60 + "\n")
    
    exit(0 if result.wasSuccessful() else 1)
