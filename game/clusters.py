"""GPU Clustering System - Drag-and-drop GPU grouping for multi-GPU jobs"""

class GPUCluster:
    """A cluster of GPUs that work together as a unit"""
    _next_id = 1
    
    def __init__(self, gpu_ids):
        """Create a cluster from a list of GPU IDs
        
        Args:
            gpu_ids: List of GPU IDs to include in cluster
        """
        self.cluster_id = GPUCluster._next_id
        GPUCluster._next_id += 1
        
        self.gpu_ids = gpu_ids
        self.current_job = None
        self.max_size = 8  # Max GPUs per cluster (like DGX H100)
    
    def can_add_gpu(self, gpu_id):
        """Check if we can add another GPU to this cluster"""
        return len(self.gpu_ids) < self.max_size and gpu_id not in self.gpu_ids
    
    def add_gpu(self, gpu_id):
        """Add a GPU to this cluster"""
        if self.can_add_gpu(gpu_id):
            self.gpu_ids.append(gpu_id)
            return True
        return False
    
    def remove_gpu(self, gpu_id):
        """Remove a GPU from this cluster"""
        if gpu_id in self.gpu_ids:
            self.gpu_ids.remove(gpu_id)
            return True
        return False
    
    def get_total_vram(self, gpus):
        """Calculate total VRAM across all GPUs in cluster"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        return sum(g.vram for g in cluster_gpus)
    
    def get_available_vram(self, gpus):
        """Calculate available VRAM (VRAM - used)"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        return sum(g.vram - g.vram_used for g in cluster_gpus)
    
    def is_available(self, gpus):
        """Check if all GPUs in cluster are available"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        return all(g.is_available() for g in cluster_gpus)
    
    def is_homogeneous(self, gpus):
        """Check if all GPUs are the same type"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        if not cluster_gpus:
            return True
        gpu_types = set(g.gpu_type for g in cluster_gpus)
        return len(gpu_types) == 1
    
    def get_gpu_types(self, gpus):
        """Get list of GPU types in this cluster"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        return [g.gpu_type for g in cluster_gpus]
    
    def get_primary_gpu_type(self, gpus):
        """Get the most common GPU type in cluster"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        if not cluster_gpus:
            return None
        from collections import Counter
        type_counts = Counter(g.gpu_type for g in cluster_gpus)
        return type_counts.most_common(1)[0][0]
    
    def to_dict(self, gpus):
        """Convert cluster to dictionary for JSON"""
        cluster_gpus = [g for g in gpus if g.gpu_id in self.gpu_ids]
        
        return {
            'id': self.cluster_id,
            'gpu_ids': self.gpu_ids,
            'size': len(self.gpu_ids),
            'total_vram': self.get_total_vram(gpus),
            'available_vram': self.get_available_vram(gpus),
            'is_available': self.is_available(gpus),
            'is_homogeneous': self.is_homogeneous(gpus),
            'gpu_types': self.get_gpu_types(gpus),
            'primary_type': self.get_primary_gpu_type(gpus),
            'has_job': self.current_job is not None
        }


class ClusterManager:
    """Manages all GPU clusters in the game"""
    
    def __init__(self):
        self.clusters = []
    
    def create_cluster(self, gpu_ids, all_gpus):
        """Create a new cluster from GPU IDs
        
        Args:
            gpu_ids: List of GPU IDs to include
            all_gpus: List of all GPU objects to validate types
            
        Returns:
            tuple: (success, cluster_id or error_message)
        """
        if not gpu_ids or len(gpu_ids) == 0:
            return False, "Need at least 2 GPUs to create cluster"
        
        if len(gpu_ids) < 2:
            return False, "Need at least 2 GPUs to create cluster"
        
        if len(gpu_ids) > 8:
            return False, "Maximum 8 GPUs per cluster"
        
        # Check if any GPUs are already in a cluster
        for cluster in self.clusters:
            for gpu_id in gpu_ids:
                if gpu_id in cluster.gpu_ids:
                    return False, f"GPU #{gpu_id} is already in a cluster"
        
        # ENFORCE SAME GPU TYPE REQUIREMENT
        cluster_gpus = [g for g in all_gpus if g.gpu_id in gpu_ids]
        gpu_types = set(g.gpu_type for g in cluster_gpus)
        
        if len(gpu_types) > 1:
            types_str = ', '.join(gpu_types)
            return False, f"Can only cluster same GPU types! ({types_str} are different)"
        
        cluster = GPUCluster(gpu_ids)
        self.clusters.append(cluster)
        
        gpu_type = list(gpu_types)[0] if gpu_types else 'Unknown'
        return True, cluster.cluster_id
    
    def add_gpu_to_cluster(self, cluster_id, gpu_id, all_gpus):
        """Add a GPU to an existing cluster"""
        # Find the cluster
        cluster = self.get_cluster(cluster_id)
        if not cluster:
            return False, "Cluster not found"
        
        # Check if GPU is already in another cluster
        for c in self.clusters:
            if gpu_id in c.gpu_ids:
                return False, f"GPU #{gpu_id} is already in cluster #{c.cluster_id}"
        
        # ENFORCE SAME GPU TYPE
        cluster_gpus = [g for g in all_gpus if g.gpu_id in cluster.gpu_ids]
        new_gpu = next((g for g in all_gpus if g.gpu_id == gpu_id), None)
        
        if cluster_gpus and new_gpu:
            existing_type = cluster_gpus[0].gpu_type
            if new_gpu.gpu_type != existing_type:
                return False, f"Can only add {existing_type} to this cluster (tried to add {new_gpu.gpu_type})"
        
        # Try to add
        if cluster.add_gpu(gpu_id):
            return True, f"Added GPU #{gpu_id} to cluster"
        else:
            return False, "Cluster is full (max 8 GPUs)"
    
    def remove_gpu_from_cluster(self, cluster_id, gpu_id):
        """Remove a GPU from a cluster"""
        cluster = self.get_cluster(cluster_id)
        if not cluster:
            return False, "Cluster not found"
        
        if cluster.remove_gpu(gpu_id):
            # If cluster is now empty, delete it
            if len(cluster.gpu_ids) == 0:
                self.clusters.remove(cluster)
            return True, f"Removed GPU #{gpu_id}"
        else:
            return False, "GPU not in this cluster"
    
    def disband_cluster(self, cluster_id):
        """Completely disband a cluster, freeing all GPUs"""
        cluster = self.get_cluster(cluster_id)
        if not cluster:
            return False, "Cluster not found"
        
        self.clusters.remove(cluster)
        return True, "Cluster disbanded"
    
    def get_cluster(self, cluster_id):
        """Get cluster by ID"""
        for cluster in self.clusters:
            if cluster.cluster_id == cluster_id:
                return cluster
        return None
    
    def get_cluster_for_gpu(self, gpu_id):
        """Find which cluster a GPU belongs to (if any)"""
        for cluster in self.clusters:
            if gpu_id in cluster.gpu_ids:
                return cluster
        return None
    
    def get_available_clusters(self, gpus, min_size=1):
        """Get all available clusters with at least min_size GPUs"""
        available = []
        for cluster in self.clusters:
            if len(cluster.gpu_ids) >= min_size and cluster.is_available(gpus):
                available.append(cluster)
        return available
    
    def get_unclustered_gpus(self, all_gpus):
        """Get list of GPU IDs that are not in any cluster"""
        clustered_ids = set()
        for cluster in self.clusters:
            clustered_ids.update(cluster.gpu_ids)
        
        return [gpu.gpu_id for gpu in all_gpus if gpu.gpu_id not in clustered_ids]
    
    def to_dict(self, gpus):
        """Convert all clusters to dictionary for JSON"""
        return {
            'clusters': [cluster.to_dict(gpus) for cluster in self.clusters],
            'total_clusters': len(self.clusters)
        }

