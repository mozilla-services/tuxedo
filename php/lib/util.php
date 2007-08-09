<?php
/**
 *  Utility funcs.
 *  @package mirror
 *  @subpackage lib
 */

/**
 *  determine float value of now
 *  @return float value of current time in seconds
 */
function microtime_float()
{
    list($usec, $sec) = explode(" ", microtime());
    return ((float)$usec + (float)$sec);
} 

/**
 *	Add a message to SESSION['messages'] array.
 *	The $_SESSION['messages'] array stores general or success messages.
 *	@param string $str message to add (optional)
 */
function set_msg($str=null)
{
	if (!empty($str))
	{
		$_SESSION['messages'][]=$str;
	}
}

/**
 *	Show messages.
 *	Iterates through $_SESSION['messages'] and displays them in a ul.
 *	@param string $class css class for message style
 */
function show_msg($class='msg')
{
	if (!empty($_SESSION['messages']) && is_array($_SESSION['messages']) && count($_SESSION['messages']) > 0)
	{
		echo ($class !== NULL) ? '<div class="'.$class.'">' : '';
		echo '<ul>';
		foreach ($_SESSION['messages'] as $message)
			echo '<li>'.$message.'</li>';
		echo '</ul>';
		echo ($class !== NULL) ? '</div>' : '';
		$ret = count($_SESSION['messages']);
	}
	else
	{
		$ret = 0;
	}
	unset($_SESSION['messages']);
	return $ret;
}

/**
 *	Add an error message to SESSION['errors'] array.
 *	The $_SESSION['errors'] array stores error messages.
 *	@param string $str message to add (optional)
 */
function set_error($str=null)
{
	if (!empty($str))
	{
		$_SESSION['errors'][]=$str;
	}
}

/**
 *	Show errors messages.
 *	Iterates through $_SESSION['errors'] and displays them in a ul.
 *	@param string $class css class for message style
 */
function show_error($class='error')
{
	if (@is_array($_SESSION['errors']) && count($_SESSION['errors']) > 0)
	{
		echo '<div class="'.$class.'">';
		echo '<ul>';
		foreach ($_SESSION['errors'] as $error)
			echo '<li>'.$error.'</li>';
		echo '</ul>';
		echo '</div>';
		$ret = count($_SESSION['errors']);
		unset($_SESSION['errors']);
	}
	else
	{
		$ret = 0;
	}
	return $ret;
}

/**
 *	Print out an varible enclosed by &lt;pre&gt; tags
 *	@param mixed $var the variable to print by print_r
 */
function debug_r(&$var)
{
	echo '<pre>';
	print_r($var);
	echo '</pre>';
}

/**
 *	Generate a random string good for passwords
 *	@param in $len the length of the password string
 *	@return string password
 */
function password_gen($len=6)
{

	$set = array( '0','1','2','3','4','5','6','7','8','9','a','e','i','o','u','y','b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','y','z' );
	$pw = '';

	while (strlen($pw) <= $len)
	{
		// random alphanum
		$char = $set[array_rand($set)];
		$pw .= $char;
	}

	return $pw;
}

/**
 * This recursive function empty values in an 'multi-dimensional' array.
 * @param mixed $needle it accepts just one value or an array of values
 * @return mixed false if an empty needle passed in, else a copy of the array with needle values replaced with empty strings
 */
function emptify_in_array($array, $needle)
{
	if ($needle == '')
		return FALSE;

	foreach ($array as $key=>$val)
	{
		if (is_array($val))
			$array[$key] = emptify_in_array($val, $needle);
		elseif (is_array($needle) && in_array($val, $needle))
			$array[$key] = '';
		elseif ($val === $needle)
			$array[$key] = '';
	}

	return $array;
}

/**
 *	This function checks for the existence of a particular row in a particular table matching a value.
 *	Use this with libdb, unless you want lots of problems.  :)
 *	@param string $table name of table
 *	@param string $column name of column containing value to match
 *	@param string $val value to match against database (goes in WHERE clause)
 *	@param string $extra (optional) any AND or ORDER BY or LIMIT or anything you want to add.
 *	@ret bool if a match exists, return true -- otherwise return false
 */
function record_exists($table,$column,$val,$extra=NULL)
{
	$result = db_query("SELECT * FROM {$table} WHERE {$column}='{$val}' {$extra}");
	if ($result&&mysql_num_rows($result)>0)
	{
		return true;
	}
	return false;
}

/**
 *	Show user tabs, based on an array.
 *	@param array $tabs array of tabs (name=>href)
 *	@param string $current name of tab to highlight	
 */
function show_tabs($tabs,$current)
{
	if ( is_array($tabs) )
	{
		echo "\n".'<div id="tabs"><ul>';
		foreach ( $tabs as $key=>$val )
		{
			if ( strtolower($key) == $current)
				echo "\n".'<li class="active-tab"><a href="'.$val.'">'.$key.'</a></li>';
			else
				echo "\n".'<li><a href="'.$val.'">'.$key.'</a></li>';
		}
		echo "\n".'</ul></div>';
	}
}

/**
 * Sort a two dimensional array based on a 'column' key
 * @param array $array the array to be sorted
 * @param mixed $key the column key to be used for sorting, an array of keys are also acceptable
 * @param mixed $order the order of the sort, either 'asc' (ascending) or 'desc' (descending), can also be an array (with matching array keys to the $key param)
 * @param bool $retain_keys option to retain the original keys; default to true
 * @param bool $case_sensitive option for a case sensitive sort; default to false
 * @return array the original array on argument errors, the sorted array on success 
 */
function array_order_by(&$array, $key=null, $order=null, $retain_keys=TRUE, $case_sensitive=FALSE)
{
	if (is_array($key) && count($key)==1)
	{
		$temp = each($key);
		$key = $temp['value'];
		$order = $order[$temp['key']];
		unset($temp);
	}
	
	if (is_array($key))
	{
		if (!is_array($order))
		{
			$order = array();
		}
		if (count($key) > count($order))
		{
			$order = array_pad($order, count($key), 'asc');
		}

		// sort it according to the first key
		$temp_sort_key = reset($key);
		$temp_order_val = $order[key($key)];
		$return_arr = array_order_by($array, $temp_sort_key, $temp_order_val, $retain_keys, $case_sensitive);
		
		// set up the arrays for the 'inner', next recursion
		$key_copy = $key;
		$order_copy = $order;
		unset($key_copy[key($key)]);
		unset($order_copy[key($key)]);
		
		// get the sorting column's value in the first row
		$temp = current($return_arr);
		$temp_prev_sort_val = $temp[$temp_sort_key];
		unset($temp);
		
		$temp_return_arr = array();
		$temp_partial_array = array();
		
		foreach ($return_arr as $return_arr_key=>$return_arr_val)
		{
			if ($return_arr_val[$temp_sort_key] == $temp_prev_sort_val)
			{
				$temp_partial_array[$return_arr_key] = $return_arr_val;
			}
			else
			{
				if ($retain_keys) 
				{
					$temp_return_arr = $temp_return_arr + array_order_by($temp_partial_array, $key_copy, $order_copy, $retain_keys, $case_sensitive);
				}
				else
				{
					$temp = array_order_by($temp_partial_array, $key_copy, $order_copy, $retain_keys, $case_sensitive);
					foreach ($temp as $temp_val)
					{
						$temp_return_arr[] = $temp_val;
					}
					unset($temp);
				}
				$temp_prev_sort_val = $return_arr_val[$temp_sort_key];
				$temp_partial_array = array();
				$temp_partial_array[$return_arr_key] = $return_arr_val;
			}
		}

		// important! if the last n $temp_prev_sort_val has the same value, then they aren't sorted and added to the temp array
		if (count($return_arr) > count($temp_return_arr))
		{
			if ($retain_keys) 
			{
				$temp_return_arr = $temp_return_arr + array_order_by($temp_partial_array, $key_copy, $order_copy, $retain_keys, $case_sensitive);
			}
			else
			{
				$temp = array_order_by($temp_partial_array, $key_copy, $order_copy, $retain_keys, $case_sensitive);
				foreach ($temp as $temp_val)
				{
					$temp_return_arr[] = $temp_val;
				}
				unset($temp);
			}
		}

		return $temp_return_arr;
	}
		
	if (empty($array) || is_null($key))
		return $array;
	
	if (!array_key_exists($key, reset($array)))
		return $array;
	
	$order =& strtolower($order);
	if ($order == '' || ($order != 'asc' && $order != 'desc'))
		$order = 'asc';
		
	// construct an array that will be used to order the keys
	foreach($array as $row_key => $row)
	{
		$x[$row_key] = $row[$key];
	}
	
	if ($case_sensitive)
		natsort($x);
	else
		natcasesort($x);
	
	if ($order == 'desc')
		$x =& array_reverse($x, TRUE);
		
	// now use those keys to order the original array
	foreach($x as $row_key => $uselessvalue)
	{
		if ($retain_keys)
			$return_arr[$row_key] =& $array[$row_key];
		else
			$return_arr[] =& $array[$row_key];
	}
	
	return $return_arr;
}

?>
