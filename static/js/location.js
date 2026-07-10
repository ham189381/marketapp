// Location management functions

function getLocation() {
    const statusDiv = document.getElementById('location_status');
    
    if (!navigator.geolocation) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-times-circle"></i> 
                Geolocation is not supported in this browser.
            </div>
        `;
        return;
    }
    
    statusDiv.innerHTML = `
        <div class="location-loading">
            <i class="fas fa-spinner fa-spin"></i> 
            Getting your location...
        </div>
    `;
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            
            // Set form values
            document.getElementById('latitude').value = latitude;
            document.getElementById('longitude').value = longitude;
            
            // Get address from coordinates (reverse geocoding)
            getAddressFromCoords(latitude, longitude);
            
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> 
                    Location captured! Latitude: ${latitude.toFixed(6)}, Longitude: ${longitude.toFixed(6)}
                </div>
            `;
        },
        function(error) {
            let errorMessage = 'Unable to get location. ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage += 'Please allow location access in your browser settings.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage += 'Location information is unavailable.';
                    break;
                case error.TIMEOUT:
                    errorMessage += 'Location request timed out.';
                    break;
                default:
                    errorMessage += 'Unknown error occurred.';
            }
            
            statusDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i> 
                    ${errorMessage}
                    <br><small>You can manually enter your location in the items description.</small>
                </div>
            `;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

function getAddressFromCoords(latitude, longitude) {
    // Using OpenStreetMap Nominatim API for reverse geocoding
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                document.getElementById('location_address').value = data.display_name;
                console.log('Address captured:', data.display_name);
            }
        })
        .catch(error => {
            console.error('Error getting address:', error);
            // Don't show error to user, as we already have coordinates
        });
}

// Function to get user location on page load (optional)
function getLocationOnLoad() {
    const autoGetLocation = document.querySelector('input[name="auto_location"]');
    if (autoGetLocation && autoGetLocation.value === 'true') {
        getLocation();
    }
}