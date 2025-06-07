#!/usr/bin/env python3
"""
Advanced ML Algorithms for Travel Reimbursement System
Testing sophisticated ML approaches not yet explored
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Try to import ML libraries (install if needed)
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from sklearn.naive_bayes import GaussianNB
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import mean_absolute_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Install with: pip install scikit-learn")

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not available. Install with: pip install tensorflow")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Install with: pip install torch")

def load_data():
    """Load and prepare the training data"""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    
    X = []
    y = []
    
    for case in cases:
        duration = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        reimbursement = case['expected_output']
        
        # Basic features
        features = [duration, miles, receipts]
        
        # Engineered features
        features.extend([
            miles / duration if duration > 0 else 0,  # miles per day
            receipts / duration if duration > 0 else 0,  # receipts per day
            miles / receipts if receipts > 0 else 0,  # efficiency ratio
            duration * miles,  # interaction
            duration * receipts,  # interaction
            miles * receipts,  # interaction
            np.log(duration + 1),  # log transforms
            np.log(miles + 1),
            np.log(receipts + 1),
            duration ** 2,  # polynomial features
            miles ** 0.5,
            receipts ** 0.5,
        ])
        
        X.append(features)
        y.append(reimbursement)
    
    return np.array(X), np.array(y)

class NeuralNetworkTensorFlow:
    """Neural Network using TensorFlow/Keras"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def fit(self, X, y):
        if not TENSORFLOW_AVAILABLE:
            return self
        
        X_scaled = self.scaler.fit_transform(X)
        
        # Build neural network
        self.model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1)
        ])
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        # Train with early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=20, restore_best_weights=True
        )
        
        self.model.fit(
            X_scaled, y,
            epochs=200,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            verbose=0
        )
        
        return self
    
    def predict(self, X):
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return np.zeros(len(X))
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled, verbose=0).flatten()

class NeuralNetworkPyTorch:
    """Neural Network using PyTorch"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def fit(self, X, y):
        if not PYTORCH_AVAILABLE:
            return self
        
        X_scaled = self.scaler.fit_transform(X)
        
        class Net(nn.Module):
            def __init__(self, input_size):
                super(Net, self).__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_size, 128),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(64, 32),
                    nn.ReLU(),
                    nn.Linear(32, 16),
                    nn.ReLU(),
                    nn.Linear(16, 1)
                )
            
            def forward(self, x):
                return self.layers(x)
        
        self.model = Net(X.shape[1])
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X_scaled)
        y_tensor = torch.FloatTensor(y).reshape(-1, 1)
        
        # Training loop
        self.model.train()
        for epoch in range(1000):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            
            if epoch % 100 == 0:
                print(f"PyTorch Epoch {epoch}, Loss: {loss.item():.4f}")
        
        return self
    
    def predict(self, X):
        if not PYTORCH_AVAILABLE or self.model is None:
            return np.zeros(len(X))
        
        X_scaled = self.scaler.transform(X)
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_scaled)
            predictions = self.model(X_tensor)
            return predictions.numpy().flatten()

class BayesianRegressor:
    """Bayesian approach using Gaussian Process"""
    
    def __init__(self):
        if SKLEARN_AVAILABLE:
            kernel = ConstantKernel(1.0) * RBF(1.0)
            self.model = GaussianProcessRegressor(
                kernel=kernel,
                alpha=1e-6,
                normalize_y=True,
                n_restarts_optimizer=10
            )
        else:
            self.model = None
    
    def fit(self, X, y):
        if self.model is not None:
            self.model.fit(X, y)
        return self
    
    def predict(self, X):
        if self.model is not None:
            return self.model.predict(X)
        return np.zeros(len(X))

class GeneticAlgorithmOptimizer:
    """Genetic Algorithm for parameter optimization"""
    
    def __init__(self, population_size=50, generations=100):
        self.population_size = population_size
        self.generations = generations
        self.best_params = None
    
    def fitness_function(self, params, X, y):
        """Evaluate fitness of parameter set"""
        try:
            # Use parameters to calculate reimbursement
            predictions = []
            for i in range(len(X)):
                duration, miles, receipts = X[i][:3]
                pred = self.calculate_with_params(duration, miles, receipts, params)
                predictions.append(pred)
            
            # Calculate fitness (negative MAE)
            mae = mean_absolute_error(y, predictions)
            return -mae
        except:
            return -1000000  # Very bad fitness for invalid params
    
    def calculate_with_params(self, duration, miles, receipts, params):
        """Calculate reimbursement using genetic algorithm parameters"""
        base_rate, mileage_rate, receipt_rate = params[:3]
        efficiency_bonus, vacation_penalty = params[3:5]
        
        # Basic calculation
        base_amount = base_rate * duration
        mileage_amount = mileage_rate * miles
        receipt_amount = receipt_rate * receipts
        
        total = base_amount + mileage_amount + receipt_amount
        
        # Apply bonuses/penalties
        efficiency = miles / duration if duration > 0 else 0
        if 180 <= efficiency <= 220:
            total += efficiency_bonus * duration
        
        if duration >= 8:
            total *= (1 - vacation_penalty)
        
        return max(0, total)
    
    def evolve(self, X, y):
        """Run genetic algorithm evolution"""
        # Initialize population
        population = []
        for _ in range(self.population_size):
            params = [
                np.random.uniform(50, 150),    # base_rate
                np.random.uniform(0.3, 0.8),   # mileage_rate
                np.random.uniform(0.4, 0.9),   # receipt_rate
                np.random.uniform(10, 50),     # efficiency_bonus
                np.random.uniform(0.05, 0.3),  # vacation_penalty
            ]
            population.append(params)
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for params in population:
                fitness = self.fitness_function(params, X, y)
                fitness_scores.append(fitness)
            
            # Selection (top 50%)
            sorted_indices = np.argsort(fitness_scores)[::-1]
            elite_size = self.population_size // 2
            elite = [population[i] for i in sorted_indices[:elite_size]]
            
            # Crossover and mutation
            new_population = elite.copy()
            while len(new_population) < self.population_size:
                parent1 = elite[np.random.randint(len(elite))]
                parent2 = elite[np.random.randint(len(elite))]
                
                # Crossover
                child = []
                for i in range(len(parent1)):
                    if np.random.random() < 0.5:
                        child.append(parent1[i])
                    else:
                        child.append(parent2[i])
                
                # Mutation
                for i in range(len(child)):
                    if np.random.random() < 0.1:  # 10% mutation rate
                        child[i] *= np.random.uniform(0.9, 1.1)
                
                new_population.append(child)
            
            population = new_population
            
            if generation % 20 == 0:
                best_fitness = max(fitness_scores)
                print(f"Generation {generation}, Best Fitness: {best_fitness:.2f}")
        
        # Return best parameters
        final_fitness = [self.fitness_function(params, X, y) for params in population]
        best_idx = np.argmax(final_fitness)
        self.best_params = population[best_idx]
        return self
    
    def predict(self, X):
        if self.best_params is None:
            return np.zeros(len(X))
        
        predictions = []
        for i in range(len(X)):
            duration, miles, receipts = X[i][:3]
            pred = self.calculate_with_params(duration, miles, receipts, self.best_params)
            predictions.append(pred)
        return np.array(predictions)

def test_advanced_ml_algorithms():
    """Test all advanced ML algorithms"""
    print("Loading data...")
    X, y = load_data()
    
    # Split data for testing
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    algorithms = {}
    
    # 1. Neural Networks
    print("\n=== Neural Networks ===")
    if TENSORFLOW_AVAILABLE:
        print("Testing TensorFlow Neural Network...")
        nn_tf = NeuralNetworkTensorFlow()
        nn_tf.fit(X_train, y_train)
        pred_tf = nn_tf.predict(X_test)
        mae_tf = mean_absolute_error(y_test, pred_tf)
        algorithms['Neural Network (TensorFlow)'] = mae_tf
        print(f"TensorFlow NN MAE: ${mae_tf:.2f}")
    
    if PYTORCH_AVAILABLE:
        print("Testing PyTorch Neural Network...")
        nn_pt = NeuralNetworkPyTorch()
        nn_pt.fit(X_train, y_train)
        pred_pt = nn_pt.predict(X_test)
        mae_pt = mean_absolute_error(y_test, pred_pt)
        algorithms['Neural Network (PyTorch)'] = mae_pt
        print(f"PyTorch NN MAE: ${mae_pt:.2f}")
    
    if SKLEARN_AVAILABLE:
        # 2. Decision Trees and Random Forest
        print("\n=== Tree-Based Methods ===")
        
        print("Testing Decision Tree...")
        dt = DecisionTreeRegressor(max_depth=10, random_state=42)
        dt.fit(X_train, y_train)
        pred_dt = dt.predict(X_test)
        mae_dt = mean_absolute_error(y_test, pred_dt)
        algorithms['Decision Tree'] = mae_dt
        print(f"Decision Tree MAE: ${mae_dt:.2f}")
        
        print("Testing Random Forest...")
        rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        pred_rf = rf.predict(X_test)
        mae_rf = mean_absolute_error(y_test, pred_rf)
        algorithms['Random Forest'] = mae_rf
        print(f"Random Forest MAE: ${mae_rf:.2f}")
        
        print("Testing Gradient Boosting...")
        gb = GradientBoostingRegressor(n_estimators=100, max_depth=6, random_state=42)
        gb.fit(X_train, y_train)
        pred_gb = gb.predict(X_test)
        mae_gb = mean_absolute_error(y_test, pred_gb)
        algorithms['Gradient Boosting'] = mae_gb
        print(f"Gradient Boosting MAE: ${mae_gb:.2f}")
        
        # 3. Support Vector Machine
        print("\n=== Support Vector Machine ===")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        svm = SVR(kernel='rbf', C=100, gamma='scale')
        svm.fit(X_train_scaled, y_train)
        pred_svm = svm.predict(X_test_scaled)
        mae_svm = mean_absolute_error(y_test, pred_svm)
        algorithms['Support Vector Machine'] = mae_svm
        print(f"SVM MAE: ${mae_svm:.2f}")
        
        # 4. K-Nearest Neighbors
        print("\n=== K-Nearest Neighbors ===")
        knn = KNeighborsRegressor(n_neighbors=10, weights='distance')
        knn.fit(X_train_scaled, y_train)
        pred_knn = knn.predict(X_test_scaled)
        mae_knn = mean_absolute_error(y_test, pred_knn)
        algorithms['K-Nearest Neighbors'] = mae_knn
        print(f"KNN MAE: ${mae_knn:.2f}")
    
    # 5. Bayesian Learning (Gaussian Process)
    print("\n=== Bayesian Learning ===")
    if SKLEARN_AVAILABLE:
        print("Testing Gaussian Process Regression...")
        # Use subset for GP (computationally expensive)
        subset_size = min(200, len(X_train))
        X_subset = X_train[:subset_size]
        y_subset = y_train[:subset_size]
        
        bayes = BayesianRegressor()
        bayes.fit(X_subset, y_subset)
        pred_bayes = bayes.predict(X_test)
        mae_bayes = mean_absolute_error(y_test, pred_bayes)
        algorithms['Gaussian Process (Bayesian)'] = mae_bayes
        print(f"Bayesian GP MAE: ${mae_bayes:.2f}")
    
    # 6. Genetic Algorithm
    print("\n=== Genetic Algorithm ===")
    print("Testing Genetic Algorithm Optimization...")
    ga = GeneticAlgorithmOptimizer(population_size=30, generations=50)
    ga.evolve(X_train, y_train)
    pred_ga = ga.predict(X_test)
    mae_ga = mean_absolute_error(y_test, pred_ga)
    algorithms['Genetic Algorithm'] = mae_ga
    print(f"Genetic Algorithm MAE: ${mae_ga:.2f}")
    print(f"Best GA Parameters: {ga.best_params}")
    
    # Summary
    print("\n" + "="*60)
    print("ADVANCED ML ALGORITHMS SUMMARY")
    print("="*60)
    
    sorted_algorithms = sorted(algorithms.items(), key=lambda x: x[1])
    for i, (name, mae) in enumerate(sorted_algorithms, 1):
        print(f"{i:2d}. {name:<30} MAE: ${mae:8.2f}")
    
    return algorithms

if __name__ == "__main__":
    test_advanced_ml_algorithms() 