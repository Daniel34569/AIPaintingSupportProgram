import cv2
import numpy as np

def calculate_length(point1, point2):
    return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def calculate_slope(point1, point2):
    return (point2[1] - point1[1]) / (point2[0] - point1[0] + np.finfo(float).eps)

def calculate_intercept(point, slope):
    return point[1] - slope * point[0]

def get_perpendicular_line(point, slope):
    perp_slope = -1 / slope
    perp_intercept = calculate_intercept(point, perp_slope)
    return perp_slope, perp_intercept

def intersect_lines(slope1, intercept1, slope2, intercept2):
    x = (intercept2 - intercept1) / (slope1 - slope2 + np.finfo(float).eps)
    y = slope1 * x + intercept1
    return [x, y]

def mosaic_roi(image, points, pixel_size=-1):
    p1, p2, p3, p4 = points

    # calculate the length of lines formed by (p1,p2) and (p3,p4)
    len1 = calculate_length(p1, p2)
    len2 = calculate_length(p3, p4)

    # Choose long side to align with the rectangle
    if len1 > len2:
        long_line = [p1, p2]
        short_line = [p3, p4]
    else:
        long_line = [p3, p4]
        short_line = [p1, p2]

    # Calculate slopes and intercepts
    long_slope = calculate_slope(long_line[0], long_line[1])
    long_intercept1 = calculate_intercept(short_line[0], long_slope)
    long_intercept2 = calculate_intercept(short_line[1], long_slope)

    perp_slope1, perp_intercept1 = get_perpendicular_line(long_line[0], long_slope)
    perp_slope2, perp_intercept2 = get_perpendicular_line(long_line[1], long_slope)

    # Get corners by intersecting lines
    # Get corners by intersecting lines
    corners = [
        intersect_lines(long_slope, long_intercept1, perp_slope1, perp_intercept1),
        intersect_lines(long_slope, long_intercept1, perp_slope2, perp_intercept2),
        intersect_lines(long_slope, long_intercept2, perp_slope1, perp_intercept1),
        intersect_lines(long_slope, long_intercept2, perp_slope2, perp_intercept2),
    ]
    #print(corners,'Corners')


    # Order corners [top-left, top-right, bottom-right, bottom-left]
    corners = np.array(corners, dtype=np.float32)
    """
    diff = np.diff(corners, axis=1)
    corners = np.array([corners[np.argmin(diff)], corners[np.argmax(diff)], corners[np.argmax(sum(diff))], corners[np.argmin(sum(diff))]], dtype=np.float32)
    """
    # Calculate center point
    center = np.mean(corners, axis=0)

    # Calculate angles from center
    angles = np.arctan2(corners[:,1]-center[1], corners[:,0]-center[0])

    # Order corners by their angle
    corners = corners[np.argsort(angles)]

    # Calculate width and height of new perspective image
    width = int(max(calculate_length(corners[0], corners[1]), calculate_length(corners[2], corners[3])))
    height = int(max(calculate_length(corners[0], corners[3]), calculate_length(corners[1], corners[2])))

    # Create destination points for perspective transform
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]], dtype=np.float32)

    # Compute perspective transformation matrix
    #print(corners.shape, 'Corners shape')
    #print(corners,'Corners')
    M = cv2.getPerspectiveTransform(corners, dst)
    Minv = cv2.getPerspectiveTransform(dst, corners) # inverse transformation

    # Warp the image to rectangle
    warped = cv2.warpPerspective(image, M, (width, height))

    # Calculate the short side of the image
    short_side = min(image.shape[0], image.shape[1])

    # If pixel size is default, set it as 1% of the short side of the image
    if pixel_size == -1:
        pixel_size = int(0.01 * short_side)
    print(f"pixel_size:{pixel_size}")

    # Ensure pixel_size is greater than 0 to avoid errors
    if pixel_size <= 0:
        raise ValueError("Pixel size must be greater than zero.")

    # Downsize ROI
    small_roi = cv2.resize(warped, (int(width / pixel_size), int(height / pixel_size)), interpolation=cv2.INTER_LINEAR)

    # Upscale to original size
    mosaic_roi = cv2.resize(small_roi, (width, height), interpolation=cv2.INTER_NEAREST)

    # Warp mosaic back to original perspective
    mosaic = cv2.warpPerspective(mosaic_roi, Minv, (image.shape[1], image.shape[0]), borderMode=cv2.BORDER_TRANSPARENT)

    # Create mask of non-black pixels (since warpPerspective can fill in black pixels)
    mask = cv2.cvtColor(mosaic, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

    # Convert single channel mask back into 3 channels
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # bitwise operations to merge mosaic and original image
    image = cv2.bitwise_and(image, 255-mask)
    image = cv2.bitwise_or(image, mosaic)

    return image