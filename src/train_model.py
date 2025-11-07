"""Train baseline XGBoost model for PCAE."""
import pandas as pd
import numpy as np
import argparse
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    roc_auc_score, average_precision_score, 
    precision_recall_curve, roc_curve
)
import matplotlib.pyplot as plt
from pathlib import Path
from utils import ensure_dir, save_model, load_config


def load_features(file_path: str) -> tuple:
    """Load features and split into X and y."""
    df = pd.read_csv(file_path)
    
    # Separate metadata and features
    metadata_cols = ['window', 'asset_ip']
    feature_cols = [col for col in df.columns if col not in metadata_cols + ['label']]
    
    X = df[feature_cols].fillna(0)
    y = df['label'] if 'label' in df.columns else pd.Series([0] * len(df))
    
    return X, y, feature_cols


def train_xgboost(X_train: pd.DataFrame, y_train: pd.Series, 
                  config: dict = None) -> xgb.XGBClassifier:
    """Train XGBoost classifier."""
    # Calculate class weights
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
    
    print(f"Training data: {pos_count} positive, {neg_count} negative")
    print(f"Scale pos weight: {scale_pos_weight:.2f}")
    
    # Default parameters
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'aucpr',
        'scale_pos_weight': scale_pos_weight,
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'tree_method': 'hist'
    }
    
    # Override with config if provided
    if config:
        params.update(config.get('model_params', {}))
    
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    return model


def evaluate_model(model: xgb.XGBClassifier, X_test: pd.DataFrame, 
                  y_test: pd.Series, output_dir: str = 'models/') -> dict:
    """Evaluate model and return metrics."""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': (y_pred == y_test).mean(),
        'roc_auc': roc_auc_score(y_test, y_pred_proba) if y_test.sum() > 0 else 0.0,
        'pr_auc': average_precision_score(y_test, y_pred_proba) if y_test.sum() > 0 else 0.0,
    }
    
    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics.update({
        'precision': report.get('1', {}).get('precision', 0.0),
        'recall': report.get('1', {}).get('recall', 0.0),
        'f1': report.get('1', {}).get('f1-score', 0.0),
    })
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    metrics['true_positives'] = int(cm[1, 1]) if cm.shape == (2, 2) else 0
    metrics['false_positives'] = int(cm[0, 1]) if cm.shape == (2, 2) else 0
    metrics['true_negatives'] = int(cm[0, 0]) if cm.shape == (2, 2) else 0
    metrics['false_negatives'] = int(cm[1, 0]) if cm.shape == (2, 2) else 0
    
    # Feature importance
    feature_importance = model.feature_importances_
    metrics['feature_importance'] = {
        'mean': float(feature_importance.mean()),
        'std': float(feature_importance.std()),
        'max': float(feature_importance.max()),
    }
    
    # Plot metrics
    ensure_dir(output_dir)
    plot_metrics(y_test, y_pred_proba, output_dir)
    
    return metrics


def plot_metrics(y_test: pd.Series, y_pred_proba: np.ndarray, output_dir: str):
    """Plot evaluation metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # ROC Curve
    if y_test.sum() > 0:
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        axes[0].plot(fpr, tpr, label='ROC Curve')
        axes[0].plot([0, 1], [0, 1], 'k--', label='Random')
        axes[0].set_xlabel('False Positive Rate')
        axes[0].set_ylabel('True Positive Rate')
        axes[0].set_title('ROC Curve')
        axes[0].legend()
        axes[0].grid(True)
        
        # Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        axes[1].plot(recall, precision, label='PR Curve')
        axes[1].set_xlabel('Recall')
        axes[1].set_ylabel('Precision')
        axes[1].set_title('Precision-Recall Curve')
        axes[1].legend()
        axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(Path(output_dir) / 'evaluation_metrics.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Metrics plots saved to {output_dir}/evaluation_metrics.png")


def main():
    parser = argparse.ArgumentParser(description='Train XGBoost model for PCAE')
    parser.add_argument('--data', type=str, default='data/features/',
                       help='Directory with feature files')
    parser.add_argument('--output', type=str, default='models/',
                       help='Output directory for model')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size (0.0-1.0)')
    
    args = parser.parse_args()
    
    ensure_dir(args.output)
    config = load_config()
    
    # Load training data
    train_file = Path(args.data) / 'train.csv'
    if not train_file.exists():
        print(f"Error: Training data not found at {train_file}")
        print("Please run feature_engineering.py first")
        return
    
    X_train, y_train, feature_cols = load_features(str(train_file))
    print(f"Loaded {len(X_train)} training samples with {len(feature_cols)} features")
    
    # Optional: Further split for validation
    if args.test_size > 0:
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=args.test_size, 
            stratify=y_train, random_state=42
        )
        print(f"Split into {len(X_train)} train and {len(X_val)} validation samples")
    else:
        X_val, y_val = X_train, y_train
    
    # Train model
    print("\nTraining XGBoost model...")
    model = train_xgboost(X_train, y_train, config)
    
    # Evaluate
    print("\nEvaluating model...")
    metrics = evaluate_model(model, X_val, y_val, args.output)
    
    # Print metrics
    print("\n" + "="*50)
    print("Model Evaluation Metrics")
    print("="*50)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    print(f"PR-AUC: {metrics['pr_auc']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1-Score: {metrics['f1']:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  TP: {metrics['true_positives']}, FP: {metrics['false_positives']}")
    print(f"  TN: {metrics['true_negatives']}, FN: {metrics['false_negatives']}")
    
    # Save model
    model_path = Path(args.output) / 'xgboost_model.pkl'
    save_model(model, str(model_path))
    print(f"\nModel saved to {model_path}")
    
    # Save feature names
    import json
    feature_info = {
        'feature_names': feature_cols,
        'metrics': {k: v for k, v in metrics.items() if not isinstance(v, (dict, list))}
    }
    with open(Path(args.output) / 'model_info.json', 'w') as f:
        json.dump(feature_info, f, indent=2)
    
    print(f"Model info saved to {args.output}/model_info.json")


if __name__ == '__main__':
    main()
