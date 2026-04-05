"""
Training script for cold storage quality prediction model.
Loads CSV data, trains RandomForest classifier, generates comprehensive metrics and visualizations.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, precision_score, recall_score, f1_score,
    accuracy_score
)
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_ENABLED = True
except ImportError:
    print("Warning: matplotlib/seaborn not installed. Skipping visualizations.")
    PLOTTING_ENABLED = False


def create_visualizations(model, X_train, X_test, y_train, y_test, X, y):
    # generate plots and save to visualizations/
    if not PLOTTING_ENABLED:
        return
    
    viz_dir = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
    os.makedirs(viz_dir, exist_ok=True)
    
    print("\ngenerating visualizations...")
    
    # heatmap
    print("generating correlation heatmap...")
    plt.figure(figsize=(10, 8))
    X_corr = X.copy()
    X_corr.columns = ['Temp', 'Humidity', 'Light', 'CO2', 'Fruit']
    X_corr['Quality'] = y
    corr = X_corr.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt='.2f', 
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'correlation_heatmap.png')}")
    
    # confusion matrix
    print("plotting confusion matrix...")
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Good', 'Bad'],
                yticklabels=['Good', 'Bad'])
    plt.ylabel('True Label', fontsize=12, fontweight='bold')
    plt.xlabel('Predicted Label', fontsize=12, fontweight='bold')
    plt.title('Confusion Matrix (Test Set)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'confusion_matrix.png')}")
    
    # ROC curve
    print("creating roc curve...")
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    plt.title('ROC Curve (Test Set)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'roc_curve.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'roc_curve.png')}")
    
    # precision-recall
    print("generating precision-recall curve...")
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2, label='Precision-Recall Curve')
    plt.xlabel('Recall', fontsize=12, fontweight='bold')
    plt.ylabel('Precision', fontsize=12, fontweight='bold')
    plt.title('Precision-Recall Curve (Test Set)', fontsize=14, fontweight='bold')
    plt.legend(loc="best")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'precision_recall_curve.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'precision_recall_curve.png')}")
    
    # feature importance bar chart
    print("plotting feature importance...")
    feature_names = ['Temp', 'Humidity', 'Light', 'CO2', 'Fruit']
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(feature_names)))
    plt.bar(range(len(importances)), importances[indices], color=colors)
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45)
    plt.ylabel('Importance', fontsize=12, fontweight='bold')
    plt.title('Feature Importance (RandomForest)', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'feature_importance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'feature_importance.png')}")
    
    # learning curve to check for overfitting
    print("generating learning curve...")
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=5, scoring='accuracy', train_sizes=np.linspace(0.1, 1.0, 10), n_jobs=-1
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_mean, 'o-', color='r', label='Training Score', linewidth=2)
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2, color='r')
    plt.plot(train_sizes, val_mean, 'o-', color='g', label='Validation Score', linewidth=2)
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2, color='g')
    plt.xlabel('Training Set Size', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
    plt.title('Learning Curve (Overfitting Detection)', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(alpha=0.3)
    plt.ylim([0.8, 1.02])
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'learning_curve.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'learning_curve.png')}")
    
    print("train vs test comparison...")
    y_pred_train = model.predict(X_train)
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred)
    
    metrics = ['Training', 'Validation']
    scores = [train_acc, test_acc]
    colors_bar = ['#2ecc71', '#3498db']
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(metrics, scores, color=colors_bar, alpha=0.8, edgecolor='black', linewidth=2)
    plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
    plt.title('Train vs Test Accuracy (Overfitting Check)', fontsize=14, fontweight='bold')
    plt.ylim([0.95, 1.001])
    for bar, score in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{score:.4f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(viz_dir, 'train_test_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Saved: {os.path.join(viz_dir, 'train_test_comparison.png')}")


def train_model():
    # train and save the quality model
    # load csv
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cold_storage_data.csv')
    df = pd.read_csv(csv_path)
    
    print(f"loaded {len(df)} rows from csv")
    # prep features and target
    X = df[['Temp', 'Humid (%)', 'Light (Fux)', 'CO2 (pmm)']].copy()
    
    # encode fruit
    fruit_encoder = LabelEncoder()
    df['Fruit_encoded'] = fruit_encoder.fit_transform(df['Fruit'])
    X['Fruit'] = df['Fruit_encoded']
    
    # target: 1 if bad, 0 if good
    y = (df['Class'].str.strip().str.upper() == 'BAD').astype(int)
    
    print(f"class distribution: {(y == 0).sum()} good, {(y == 1).sum()} bad")
    
    # split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"split: {len(X_train)} train, {len(X_test)} test")
    
    # train the model
    print("training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, max_depth=15)
    model.fit(X_train, y_train)
    
    # cross-validation
    print("running 5-fold cv...")
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"mean cv score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    
    # train predictions
    y_pred_train = model.predict(X_train)
    train_acc = accuracy_score(y_train, y_pred_train)
    
    # test predictions
    y_pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    
    gap = train_acc - test_acc
    print(f"train acc: {train_acc:.4f}, test acc: {test_acc:.4f}")
    
    if gap > 0.05:
        print(f"warning: possible overfitting, gap={gap:.4f}")
    else:
        print("+ good generalization")
    
    # detailed metrics
    print(classification_report(y_test, y_pred, target_names=['Good', 'Bad'], digits=4))
    roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"roc-auc: {roc_auc:.4f}")
    
    print("\nfeature importances:")
    feature_names = ['Temp', 'Humid (%)', 'Light (Fux)', 'CO2 (pmm)', 'Fruit']
    for name, importance in zip(feature_names, model.feature_importances_):
        bar = '█' * int(importance * 50)
        print(f"  {name:15} {bar} {importance:.4f}")
    
    # save artifacts
    model_path = os.path.join(os.path.dirname(__file__), 'quality_model.pkl')
    encoder_path = os.path.join(os.path.dirname(__file__), 'fruit_encoder.pkl')
    joblib.dump(model, model_path)
    joblib.dump(fruit_encoder, encoder_path)
    print("saving model and encoder...")
    
    create_visualizations(model, X_train, X_test, y_train, y_test, X, y)
    print("done.")


if __name__ == '__main__':
    train_model()
