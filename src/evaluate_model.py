"""Evaluate trained model on test data."""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from utils import load_model, load_config
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score,
    precision_recall_curve, roc_curve
)
import matplotlib.pyplot as plt


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series, output_dir: str = 'models/'):
    """Evaluate model on test data."""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    print("="*50)
    print("Test Set Evaluation")
    print("="*50)
    
    print(f"\nTest set size: {len(X_test)}")
    print(f"Positive samples: {y_test.sum()} ({y_test.mean()*100:.2f}%)")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(f"                Predicted")
    print(f"              Neg    Pos")
    print(f"Actual Neg    {cm[0,0]:4d}  {cm[0,1]:4d}")
    print(f"       Pos    {cm[1,0]:4d}  {cm[1,1]:4d}")
    
    # ROC and PR metrics
    if y_test.sum() > 0:
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        pr_auc = average_precision_score(y_test, y_pred_proba)
        
        print(f"\nROC-AUC: {roc_auc:.4f}")
        print(f"PR-AUC: {pr_auc:.4f}")
        
        # Plot curves
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        axes[0].plot(fpr, tpr, label=f'ROC (AUC={roc_auc:.3f})')
        axes[0].plot([0, 1], [0, 1], 'k--', label='Random')
        axes[0].set_xlabel('False Positive Rate')
        axes[0].set_ylabel('True Positive Rate')
        axes[0].set_title('ROC Curve')
        axes[0].legend()
        axes[0].grid(True)
        
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        axes[1].plot(recall, precision, label=f'PR (AUC={pr_auc:.3f})')
        axes[1].set_xlabel('Recall')
        axes[1].set_ylabel('Precision')
        axes[1].set_title('Precision-Recall Curve')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        output_path = Path(output_dir) / 'test_evaluation.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"\nPlots saved to {output_path}")
    else:
        print("\nWarning: No positive samples in test set, cannot calculate ROC/PR metrics")
    
    return {
        'accuracy': (y_pred == y_test).mean(),
        'confusion_matrix': cm.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description='Evaluate trained model')
    parser.add_argument('--model', type=str, required=True,
                       help='Path to trained model file')
    parser.add_argument('--test', type=str, required=True,
                       help='Path to test data CSV')
    parser.add_argument('--output', type=str, default='models/',
                       help='Output directory for plots')
    
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model from {args.model}...")
    model = load_model(args.model)
    
    # Load test data
    print(f"Loading test data from {args.test}...")
    df = pd.read_csv(args.test)
    
    # Separate features and labels
    metadata_cols = ['window', 'asset_ip']
    feature_cols = [col for col in df.columns if col not in metadata_cols + ['label']]
    
    X_test = df[feature_cols].fillna(0)
    y_test = df['label'] if 'label' in df.columns else pd.Series([0] * len(df))
    
    print(f"Test data: {len(X_test)} samples, {len(feature_cols)} features")
    
    # Evaluate
    evaluate_model(model, X_test, y_test, args.output)
    
    print("\nEvaluation complete!")


if __name__ == '__main__':
    main()

